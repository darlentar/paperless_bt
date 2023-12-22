import itertools
from collections import defaultdict
from typing import Callable

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .address_api import (
    AddressAPIError,
    parse_address_api_response,
    request_address_api,
)
from .coordinates import nearest_from
from .mobile_site import (
    MobileSiteGPS,
    ProviderResolver,
    read_mnc,
    read_mobile_site_gps,
)


class NearestMobileSiteOut(BaseModel):
    provider: str
    has_2g: bool
    has_3g: bool
    has_4g: bool


class NearestMobileSiteFullOut(BaseModel):
    provider: str
    coordinates: tuple[float, float]
    has_2g: bool
    has_3g: bool
    has_4g: bool


class NearestMobileSitesOut(BaseModel):
    site: list[NearestMobileSiteOut]


class NearestMobileSitesFullOut(BaseModel):
    site: list[NearestMobileSiteFullOut]


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
            full: bool = False,
        ) -> NearestMobileSitesOut | NearestMobileSitesFullOut:
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

            def nearest_mobile_site_by_provider(
                predicate: Callable[[MobileSiteGPS], bool],
            ):
                res = {}
                for provider in self.mobile_sites_by_providers:
                    nearest = nearest_from(
                        (search_site_coordinates[0], search_site_coordinates[1]),
                        (
                            site
                            for site in self.mobile_sites_by_providers[provider]
                            if predicate(site)
                        ),
                        lambda mobile_site: (mobile_site.gps[0], mobile_site.gps[1]),
                    )
                    if nearest:
                        res[provider] = nearest
                return res

            nearest_2g_mobile_site_by_providers = nearest_mobile_site_by_provider(
                lambda m: m.has_2g
            )
            nearest_3g_mobile_site_by_providers = nearest_mobile_site_by_provider(
                lambda m: m.has_3g
            )
            nearest_4g_mobile_site_by_providers = nearest_mobile_site_by_provider(
                lambda m: m.has_4g
            )

            if full:
                return NearestMobileSitesFullOut(
                    site=[
                        NearestMobileSiteFullOut(
                            provider=self.provider_resolver.resolve(
                                mobile_site.provider
                            ),
                            coordinates=(mobile_site.gps[0], mobile_site.gps[1]),
                            has_2g=mobile_site.has_2g,
                            has_3g=mobile_site.has_3g,
                            has_4g=mobile_site.has_4g,
                        )
                        for mobile_site in itertools.chain(
                            nearest_2g_mobile_site_by_providers.values(),
                            nearest_3g_mobile_site_by_providers.values(),
                            nearest_4g_mobile_site_by_providers.values(),
                        )
                    ]
                )
            else:
                return NearestMobileSitesOut(
                    site=[
                        NearestMobileSiteOut(
                            provider=self.provider_resolver.resolve(
                                mobile_site.provider
                            ),
                            has_2g=mobile_site.has_2g,
                            has_3g=mobile_site.has_3g,
                            has_4g=mobile_site.has_4g,
                        )
                        for mobile_site in itertools.chain(
                            nearest_2g_mobile_site_by_providers.values(),
                            nearest_3g_mobile_site_by_providers.values(),
                            nearest_4g_mobile_site_by_providers.values(),
                        )
                    ]
                )

        return router
