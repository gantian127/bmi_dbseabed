from __future__ import annotations

import os

import pytest
import xarray
from bmi_dbseabed import DbSeabed


@pytest.fixture
def dbseabed_instance():
    return DbSeabed()


def test_invalid_var_name(dbseabed_instance):
    with pytest.raises(ValueError, match="Please provide a valid var_name value."):
        dbseabed_instance.get_data(
            var_name="error",
            west=-98,
            south=18.0,
            east=--80,
            north=31,
            output="test.tif",
        )


@pytest.mark.parametrize(
    "west, south, east, north",
    [(-80, 18.0, -98, 31), (-98, 31, -80, 18.0)],  # west > east  # south > north
)
def test_invalid_bounding_box(west, south, east, north, dbseabed_instance):
    with pytest.raises(ValueError):
        dbseabed_instance.get_data(
            "carbonate",
            west=west,
            south=south,
            east=east,
            north=north,
            output="test.tif",
        )


def test_invalid_output(dbseabed_instance):
    with pytest.raises(ValueError):
        dbseabed_instance.get_data(
            "carbonate",
            west=-66.8,
            south=18.0,
            east=-66.2,
            north=18.4,
            output="error",
        )


# test data download for all variables
@pytest.mark.parametrize(
    "var_name",
    [
        "carbonate",
        "carbonate_totlsu",
        "grainsize",
        "grainsize_totlsu",
        "gravel",
        "gravel_totlsu",
        "mud",
        "mud_totlsu",
        "organic_carbon",
        "organic_carbon_totlsu",
        "rock",
        "rock_totlsu",
        "sand",
        "sand_totlsu",
    ],
)
@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_data_download(var_name, tmpdir):
    output_name = os.path.join(tmpdir, f"{var_name}.tif")
    data = DbSeabed().get_data(
        var_name=var_name,
        west=-98,
        south=18.0,
        east=-80,
        north=31,
        output=output_name,
    )

    assert isinstance(data, xarray.core.dataarray.DataArray)
    assert os.path.isfile(output_name) is True


# test loading local file
@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_load_local_file(tmpdir, dbseabed_instance):
    dbseabed_instance.get_data(
        "carbonate",
        west=-98,
        south=18.0,
        east=-80,
        north=31,
        output=os.path.join(tmpdir, "test.tif"),
    )
    file1_info = os.path.getmtime(os.path.join(tmpdir, "test.tif"))
    assert len(os.listdir(tmpdir)) == 1

    dbseabed_instance.get_data(
        "carbonate",
        west=-98,
        south=18.0,
        east=-80,
        north=31,
        output=os.path.join(tmpdir, "test.tif"),
        local_file=True,
    )
    file2_info = os.path.getmtime(os.path.join(tmpdir, "test.tif"))

    assert file1_info == file2_info
