# -*- coding: utf-8 -*-
from typing import List

from aiohttp import web
from pydantic import BaseModel
from unittest.mock import patch

import pytest

from patchwork.contrib.common import HTTPConnector
from patchwork.contrib.common.connector import ConnectorError


class TestModel(BaseModel):
    pass


@pytest.mark.asyncio
async def test_response_no_content(aiohttp_raw_server):

    async def handler(request):
        return web.Response(status=204)

    data_endpoint = await aiohttp_raw_server(handler)
    await data_endpoint.start_server()

    connector = HTTPConnector(endpoint_url=str(data_endpoint.make_url('/')))

    async with connector:
        response = await connector.send('get', '/', response_model=None)
        assert response is None

        with pytest.raises(ConnectorError):
            # expected model, got No content response
            response = await connector.send('get', '/', response_model=TestModel)


@pytest.mark.asyncio
async def test_expected_model(aiohttp_raw_server):

    async def handler(request):
        return web.json_response({})

    data_endpoint = await aiohttp_raw_server(handler)
    await data_endpoint.start_server()

    connector = HTTPConnector(endpoint_url=str(data_endpoint.make_url('/')))

    async with connector:
        response = await connector.send('get', '/', response_model=TestModel)
        assert isinstance(response, TestModel)

        with pytest.raises(ConnectorError):
            # empty response expected, got content
            response = await connector.send('get', '/', response_model=None)


@pytest.mark.asyncio
async def test_expected_list(aiohttp_raw_server):

    async def handler(request):
        return web.json_response([{}, {}])

    data_endpoint = await aiohttp_raw_server(handler)
    await data_endpoint.start_server()

    connector = HTTPConnector(endpoint_url=str(data_endpoint.make_url('/')))

    async with connector:
        response = await connector.send('get', '/', response_model=List[TestModel])
        assert isinstance(response, list)
        assert len(response) == 2
        assert isinstance(response[0], TestModel) and isinstance(response[1], TestModel)
