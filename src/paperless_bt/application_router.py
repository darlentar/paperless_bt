from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .address_api import (
    AddressAPIError,
    parse_address_api_response,
    request_address_api,
)
from .mobile_site import (
    MobileSiteGPS,
    ProviderResolver,
    UnknownProvider,
    filter_reachable_mobile_sites,
    read_mnc,
    read_mobile_site_gps,
)


class NearestMobileSiteFullOut(BaseModel):
    coordinates: tuple[float, float]


class NearestMobileSitesOut(BaseModel):
    site: dict[str, dict[str, int]]


class NearestMobileSitesFullOut(BaseModel):
    site: dict[str, dict[str, list[NearestMobileSiteFullOut]]]


def reachable_mobiles_sites_to_out(
    reachable_sites: dict[str, dict[str, list[MobileSiteGPS]]],
) -> NearestMobileSitesOut:
    site = {
        provider: {
            protocol: len(sites) for protocol, sites in sites_by_protocol.items()
        }
        for provider, sites_by_protocol in reachable_sites.items()
    }
    return NearestMobileSitesOut(site=site)


def reachable_mobiles_sites_to_full_out(
    reachable_sites: dict[str, dict[str, list[MobileSiteGPS]]],
) -> NearestMobileSitesFullOut:
    site = {
        provider: {
            protocol: [
                NearestMobileSiteFullOut(
                    coordinates=(site.gps[0], site.gps[1]),
                )
                for site in sites
            ]
            for protocol, sites in sites_by_protocol.items()
        }
        for provider, sites_by_protocol in reachable_sites.items()
    }
    return NearestMobileSitesFullOut(site=site)


class ApplicationRouterBuilder:
    def __init__(self, mnc_csv: str, mobile_sites_gps_csv: str):
        mobile_sites = read_mobile_site_gps(mobile_sites_gps_csv)
        brand_mobile_codes = read_mnc(mnc_csv)

        self.provider_resolver = ProviderResolver(
            mobile_sites=mobile_sites,
            brand_mobile_codes=brand_mobile_codes,
        )
        self.mobile_sites = mobile_sites

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

            reachable_mobiles_sites = filter_reachable_mobile_sites(
                (search_site_coordinates[0], search_site_coordinates[1]),
                self.mobile_sites,
            )

            reachable_mobiles_sites_with_resolved_provider = {}
            for provider, sites_by_protocol in reachable_mobiles_sites.items():
                try:
                    provider = self.provider_resolver.resolve(provider)
                except UnknownProvider:
                    provider = provider
                reachable_mobiles_sites_with_resolved_provider[
                    provider
                ] = sites_by_protocol

            if full:
                return reachable_mobiles_sites_to_full_out(
                    reachable_mobiles_sites_with_resolved_provider
                )
            else:
                return reachable_mobiles_sites_to_out(
                    reachable_mobiles_sites_with_resolved_provider
                )

        return router
