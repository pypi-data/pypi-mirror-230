# -*- coding: utf-8 -*-
from importlib.metadata import version

import aiohttp
import json
import sys
from pydantic import BaseModel
from typing import Literal, Union, Type, Any, TypeVar, List, get_args, get_origin

from patchwork.core import Component

try:
    from prometheus_client import Histogram, Info
except ImportError:
    from patchwork.core.stubs.prometheus import Histogram, Info, DummyMetric


request_time = Histogram('connector_request_time', "Connector endpoint time", ["method", "url", "user_agent", "version"])
conn_info = Info("connector_endpoint_info", "Connector endpoint info")


class ConnectorError(Exception):
    pass


class ConnectorResponseError(ConnectorError):
    def __init__(self, code):
        self.code = code


class ConnectorBadData(ConnectorResponseError):
    def __init__(self, response):
        self.response = response
        super().__init__(code=422)


class ConnectorForbidden(ConnectorResponseError):
    def __init__(self):
        super().__init__(code=403)


class ConnectorNotFound(ConnectorResponseError):
    def __init__(self):
        super().__init__(code=404)


class ConnectorTooManyAttempts(ConnectorResponseError):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(code=429)


T = TypeVar('T')


class PrometheusMixin:

    settings: Any
    connector_version: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if Histogram is DummyMetric:
            raise RuntimeError("unable to use prometheus metrics mixin without Prometheus Client installed")

        conn_info.info({
            "version": self.connector_version,
            "user_agent": self.settings.user_agent,
            "endpoint_url": self.settings.endpoint_url,
            "timeout": self.settings.timeout
        })

    async def send(
            self,
            method: Literal['get', 'head', 'post', 'put', 'patch', 'delete'],
            url: str = '/',
            *,
            payload: BaseModel = None,
            response_model: Type[T] = Any,
            **options,
    ) -> Union[T, None]:
        with request_time.labels(
            method=method,
            url=url,
            user_agent=self.settings.user_agent,
            version=self.connector_version
        ).time():
            return await super().send(method, url, payload=payload, response_model=response_model, **options)


class HTTPConnector(Component):

    class Config(Component.Config):
        timeout: int = 60
        max_conn_limit: int = 100
        user_agent: str = None
        endpoint_url: str

    session: aiohttp.ClientSession
    connector_version = version('patchwork-contrib') if 'patchwork-contrib' in sys.modules else ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._timeout = aiohttp.ClientTimeout(total=self.settings.timeout)

    async def _start(self) -> bool:
        connector = aiohttp.TCPConnector(limit=self.settings.max_conn_limit)

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.settings.user_agent:
            headers['user-agent'] = self.settings.user_agent

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self._timeout,
            headers=headers,
            base_url=self.settings.endpoint_url,
            raise_for_status=False,
            cookie_jar=aiohttp.DummyCookieJar()     # do not store any cookies for inter-services communication
        )
        return True

    async def _stop(self) -> bool:
        await self.session.close()
        return False

    async def send(
            self,
            method: Literal['get', 'head', 'post', 'put', 'patch', 'delete'],
            url: str = '/',
            *,
            payload: BaseModel = None,
            response_model: Type[T] = Any,
            **options,
    ) -> Union[T, None]:

        if payload is not None:
            # use pydantic JSON encoder instead of aiohttp, as pydantic one supports all types
            # supported by pydantic
            payload = payload.json().encode('utf-8')

        if method == 'get':
            assert payload is None, \
                'payload forbidden on GET method'
            response = await self.session.get(url, **options)
        elif method == 'head':
            assert payload is None, \
                'payload forbidden on HEAD method'
            response = await self.session.head(url, **options)
        elif method == 'post':
            response = await self.session.post(url, data=payload, **options)
        elif method == 'put':
            response = await self.session.put(url, data=payload, **options)
        elif method == 'patch':
            response = await self.session.patch(url, data=payload, **options)
        elif method == 'delete':
            assert payload is None, \
                "payload is forbidden on DELETE method"
            response = await self.session.delete(url, **options)
        else:
            raise NotImplementedError('not supported HTTP method')

        try:
            return await self._handle_response(response, response_model)
        except ConnectorResponseError:
            # response errors just re-raise
            raise
        except Exception as e:
            raise ConnectorError() from e
        finally:
            if not response.closed:
                response.close()

    async def _handle_response(
            self,
            response: aiohttp.ClientResponse,
            response_model: Union[Type[BaseModel], Any, None, List[BaseModel]]
    ) -> Union[BaseModel, List[BaseModel], None]:

        if response.status in {200, 201, 202}:
            if response_model is Any:
                return None
            elif response_model is None:
                if response.content_length is not None:
                    raise ValueError('empty response expected')
                return None

            if not response.content_length:
                raise ValueError('missing data')

            data = await response.read()
            if response.content_type == 'application/json':
                data = json.loads(data)

            orig = get_origin(response_model)
            if orig is list:
                if not isinstance(data, list):
                    raise ValueError("list is expected, but endpoint returned not a list")

                model = get_args(response_model)[0]
                return [model(**d) for d in data]

            return response_model(**data)
        elif response.status == 204:
            if response_model is not Any and response_model is not None:
                raise ValueError('response data expected, but 204 No Content response received')
            return None
        elif response.status == 403:
            raise ConnectorForbidden()
        elif response.status == 404:
            raise ConnectorNotFound()
        elif response.status == 422:
            raise ConnectorBadData(await response.json())
        elif response.status == 429:
            raise ConnectorTooManyAttempts(int(response.headers.get('Retry-After', '0')))
        else:
            raise ConnectorResponseError(code=response.status)
