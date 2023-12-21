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


@pytest.mark.http_request
@pytest.mark.asyncio
async def test_request_address_api():
    response = await request_address_api(search="8+bd+du+port")
    assert isinstance(response, str)
    # we just check that response is a FeatureCollection if parsing failed
    # it raises an error.
    assert isinstance(parse_address_api_response(response), FeatureCollection)


@pytest.mark.asyncio
async def test_request_address_api_not_200():
    with patch("aiohttp.ClientSession.get") as mock:
        mock.return_value.__enter__.return_value = 400
        with pytest.raises(AddressAPIError):
            await request_address_api(search="8+bd+du+port")
