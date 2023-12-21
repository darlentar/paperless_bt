import asyncio
import csv
from collections import defaultdict
from functools import wraps

import click
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from .address_api import (
    AddressAPIError,
    parse_address_api_response,
    request_address_api,
)
from .coordinates import compute_haversine, nearest_from
from .mobile_site import (
    MobileSiteGPS,
    ProviderResolver,
    convert_lanbert93_to_gps,
    read_mnc,
    read_mobile_site,
    read_mobile_site_gps,
)

app = FastAPI()


class NearestMobileSiteOut(BaseModel):
    provider: str
    has_2g: bool
    has_3g: bool
    has_4g: bool


class NearestMobileSitesOut(BaseModel):
    site: list[NearestMobileSiteOut]


@click.group()
def cli():
    pass


def get_mobile_sites() -> dict[str, list[MobileSiteGPS]]:
    mobile_sites = read_mobile_site_gps("site_mobiles_gps.csv")
    mobile_sites_by_providers = defaultdict(list)
    for mobile_site in mobile_sites:
        mobile_sites_by_providers[mobile_site.provider].append(mobile_site)
    return mobile_sites_by_providers


def get_provider_resolver(mobile_sites=Depends(get_mobile_sites)) -> ProviderResolver:
    brand_mobile_codes = read_mnc("french_mnc.csv")
    return ProviderResolver(
        mobile_sites=mobile_sites,
        brand_mobile_codes=brand_mobile_codes,
    )


@app.get("/")
async def root(
    search: str,
    mobile_sites_by_providers=Depends(get_mobile_sites),
    provider_resolver=Depends(get_provider_resolver),
) -> NearestMobileSitesOut:
    # TODO: What happend when there is no features
    try:
        first_feature = parse_address_api_response(
            await request_address_api(search)
        ).features[0]
    # something bad happened to know gps cooardinates so give up early
    except AddressAPIError:
        raise HTTPException(status_code=500, detail="Can't found GPS coordinates.")
    search_site_coordinates = first_feature.geometry.coordinates
    nearest_mobile_site_by_providers = {}
    for provider in mobile_sites_by_providers:
        nearest_mobile_site_by_providers[provider] = nearest_from(
            (search_site_coordinates[0], search_site_coordinates[1]),
            iter(mobile_sites_by_providers[provider]),
            lambda mobile_site: (mobile_site.gps[0], mobile_site.gps[1]),
        )

    return NearestMobileSitesOut(
        site=[
            NearestMobileSiteOut(
                provider=provider_resolver.resolve(mobile_site.provider),
                has_2g=mobile_site.has_2g,
                has_3g=mobile_site.has_3g,
                has_4g=mobile_site.has_4g,
            )
            for mobile_site in nearest_mobile_site_by_providers.values()
            if compute_haversine(
                mobile_site.gps[0],
                search_site_coordinates[0],
                mobile_site.gps[1],
                search_site_coordinates[1],
            )
            < 10_000e3
        ]
    )


def async_cmd(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))

    return wrapper


@cli.command()
@async_cmd
async def run():
    """Run the server."""
    config = uvicorn.Config(
        "paperless_bt.main:app",
        port=5000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


@cli.command()
def generate():
    """Generate mobile site from lamber 93 coordinates to GPS."""
    mobile_sites = read_mobile_site("site_mobiles.csv")
    with open("site_mobiles_gps.csv", "w", newline="") as f:
        mobile_site_csv_writter = csv.writer(f, delimiter=" ", quotechar='"')
        for mobile_site in mobile_sites:
            mobile_site = convert_lanbert93_to_gps(mobile_site)
            mobile_site_csv_writter.writerow(
                [
                    mobile_site.provider,
                    mobile_site.gps[0],
                    mobile_site.gps[1],
                    mobile_site.has_2g,
                    mobile_site.has_3g,
                    mobile_site.has_4g,
                ]
            )


if __name__ == "__main__":
    asyncio.run(cli())
