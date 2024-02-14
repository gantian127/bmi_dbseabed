from __future__ import annotations

import os

import click

from ._version import __version__
from .dbseabed import DbSeabed


@click.command()
@click.version_option(version=__version__)
@click.option(
    "--var_name",
    required=True,
    help="Variable name of the dataset.",
)
@click.option(
    "--bbox",
    required=True,
    help=(
        "Bounding box for data download."
        " Values are based on the crs (EPSG 4326) in a sequence of west, south, east,"
        " north separated by comma."
    ),
)
@click.argument("output", type=click.Path(exists=False))
def main(
    var_name,
    bbox,
    output,
):
    west, south, east, north = list(map(float, bbox.split(",")))
    DbSeabed().get_data(
        var_name=var_name,
        west=west,
        south=south,
        east=east,
        north=north,
        output=output,
        local_file=False,
    )
    if os.path.isfile(output):
        print("Done")
