from collections import namedtuple
from unittest.mock import patch

import pytest
from paperless_bt.address_api import (
    AddressAPIError,
    Feature,
    FeatureCollection,
    Geometry,
    Properties,
    parse_address_api_response,
    request_address_api,
)


@pytest.fixture
def address_api_json() -> str:
    with open("address_api.json") as f:
        content = f.read()
    return content


def test_parse_address_api_response(address_api_json):
    assert parse_address_api_response(address_api_json).features[0] == Feature(
        geometry=Geometry(coordinates=[2.290084, 49.897442]),
        properties=Properties(
            label="8 Boulevard du Port 80000 Amiens",
            x=648952.58,
            y=6977867.14,
        ),
    )


def test_parse_address_api_response_not_valid():
    with pytest.raises(AddressAPIError) as ex:
        parse_address_api_response("PLOP")
    assert "could not parse response" in str(ex.value)


@pytest.mark.http_request
@pytest.mark.asyncio
async def test_request_address_api():
    response = await request_address_api(search="8+bd+du+port")
    assert isinstance(response, str)
    # we just check that response is a FeatureCollection if parsing failed
    # it raises an error.
    assert isinstance(parse_address_api_response(response), FeatureCollection)


class WithAiohttpContext:
    async def __aenter__(self, *args, **kwargs):
        Response = namedtuple("Response", ["status", "reason"])
        return Response(status=400, reason="Not Found")

    async def __aexit__(self, *args, **kwargs):
        pass


@pytest.mark.asyncio
async def test_request_address_api_not_200():
    with patch("aiohttp.ClientSession.get") as mock:
        mock.return_value = WithAiohttpContext()
        with pytest.raises(AddressAPIError) as ex:
            await request_address_api(search="8+bd+du+port")
        assert "could not make http request" in str(ex.value)
        assert "400" in str(ex.value)
