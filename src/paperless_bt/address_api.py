from pydantic import BaseModel, ConfigDict


class Geometry(BaseModel):
    model_config = ConfigDict(strict=True)

    coordinates: list[float]


class Properties(BaseModel):
    model_config = ConfigDict(strict=True)

    label: str
    x: float
    y: float


class Feature(BaseModel):
    model_config = ConfigDict(strict=True)

    geometry: Geometry
    properties: Properties


class FeatureCollection(BaseModel):
    model_config = ConfigDict(strict=True)

    features: list[Feature]


def parse_address_api_response(response: str) -> FeatureCollection:
    return FeatureCollection.model_validate_json(response)
