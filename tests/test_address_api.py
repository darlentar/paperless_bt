import pytest
from paperless_bt.address_api import (
    Feature,
    Geometry,
    Properties,
    parse_address_api_response,
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
