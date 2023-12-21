from collections import defaultdict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .address_api import (
    AddressAPIError,
    parse_address_api_response,
    request_address_api,
)
from .coordinates import compute_haversine, nearest_from
from .mobile_site import (
    ProviderResolver,
    read_mnc,
    read_mobile_site_gps,
)

MAX_DISTANCE_AUTHORIZED = 10e3


class NearestMobileSiteOut(BaseModel):
    provider: str
    has_2g: bool
    has_3g: bool
    has_4g: bool


class NearestMobileSitesOut(BaseModel):
    site: list[NearestMobileSiteOut]


class ApplicationRouterBuilder:
    def __init__(self, mnc_csv: str, mobile_sites_gps_csv: str):
        mobile_sites = read_mobile_site_gps(mobile_sites_gps_csv)
        brand_mobile_codes = read_mnc(mnc_csv)

        self.provider_resolver = ProviderResolver(
            mobile_sites=mobile_sites,
            brand_mobile_codes=brand_mobile_codes,
        )
        mobile_sites_by_providers = defaultdict(list)
        for mobile_site in mobile_sites:
            mobile_sites_by_providers[mobile_site.provider].append(mobile_site)
        self.mobile_sites_by_providers = mobile_sites_by_providers

    def build(self) -> APIRouter:
        router = APIRouter()

        @router.get("/")
        async def root(
            search: str,
        ) -> NearestMobileSitesOut:
            try:
                first_feature = parse_address_api_response(
                    await request_address_api(search)
                ).features[0]
            # something bad happened to know gps cooardinates so give up early
            except (AddressAPIError, IndexError):
                raise HTTPException(
                    status_code=500,
                    detail="Can't found GPS coordinates.",
                )
            search_site_coordinates = first_feature.geometry.coordinates
            nearest_mobile_site_by_providers = {}
            for provider in self.mobile_sites_by_providers:
                nearest_mobile_site_by_providers[provider] = nearest_from(
                    (search_site_coordinates[0], search_site_coordinates[1]),
                    iter(self.mobile_sites_by_providers[provider]),
                    lambda mobile_site: (mobile_site.gps[0], mobile_site.gps[1]),
                )

            return NearestMobileSitesOut(
                site=[
                    NearestMobileSiteOut(
                        provider=self.provider_resolver.resolve(mobile_site.provider),
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
                    < MAX_DISTANCE_AUTHORIZED
                ]
            )

        return router
