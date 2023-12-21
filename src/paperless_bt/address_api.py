import aiohttp
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


class AddressAPIError(Exception):
    pass


async def request_address_api(search: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api-adresse.data.gouv.fr/search/?q={search}"
        ) as response:
            if response.status != 200:
                raise AddressAPIError
            return await response.text()
