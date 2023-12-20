from paperless_bt.address_api import (
    Feature,
    Geometry,
    Properties,
    parse_address_api_response,
)


def test_parse_address_api_response():
    with open("address_api.json") as f:
        content = f.read()
    assert parse_address_api_response(content).features[0] == Feature(
        geometry=Geometry(coordinates=[2.290084, 49.897442]),
        properties=Properties(
            label="8 Boulevard du Port 80000 Amiens",
            x=648952.58,
            y=6977867.14,
        ),
    )
