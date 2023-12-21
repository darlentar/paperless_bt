import asyncio
import csv
from functools import wraps

import click
import uvicorn
from fastapi import FastAPI

from .application_router import ApplicationRouterBuilder
from .mobile_site import (
    convert_lanbert93_to_gps,
    read_mobile_site,
)

app = FastAPI()


@click.group()
def cli():
    import logging

    logging.basicConfig(format="[%(asctime)s] %(filename)s->%(funcName)s: %(message)s")


def async_cmd(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))

    return wrapper


@cli.command()
@click.argument("mnc_csv", type=click.Path(exists=True))
@click.argument("mobile_site_gps_csv", type=click.Path(exists=True))
@async_cmd
async def run(mnc_csv, mobile_site_gps_csv):
    """Run the server."""
    app.include_router(
        ApplicationRouterBuilder(
            mnc_csv,
            mobile_site_gps_csv,
        ).build()
    )
    config = uvicorn.Config(
        app,
        port=5000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def generate(input, output):
    """Generate mobile site from lamber 93 coordinates to GPS."""
    mobile_sites = read_mobile_site(input)
    with open(output, "w", newline="") as f:
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
