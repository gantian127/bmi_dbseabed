from __future__ import annotations

import os

import pytest
import xarray
from bmi_dbseabed import DbSeabed


# test user input for get_data()
def test_var_name():
    with pytest.raises(ValueError):
        DbSeabed().get_data(
            "error",
            west=-66.8,
            south=18.0,
            east=-66.2,
            north=18.4,
            output="test.tif",
        )


def test_bounding_box():
    with pytest.raises(ValueError):  # west > east
        DbSeabed().get_data(
            "carbonate",
            west=-66.2,
            south=18.0,
            east=-66.8,
            north=18.4,
            output="test.tif",
        )

    with pytest.raises(ValueError):  # south > north
        DbSeabed().get_data(
            "carbonate",
            west=-66.8,
            south=18.4,
            east=-66.2,
            north=18.0,
            output="test.tif",
        )


def test_output():
    with pytest.raises(ValueError):
        DbSeabed().get_data(
            "carbonate",
            west=-66.8,
            south=18.0,
            east=-66.2,
            north=18.4,
            output="error",
        )


# test data download for get_data()
@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_data_download(tmpdir):
    data = DbSeabed().get_data(
        "carbonate",
        west=-66.8,
        south=18.0,
        east=-66.2,
        north=18.4,
        output=os.path.join(tmpdir, "test.tif"),
    )

    assert isinstance(data, xarray.core.dataarray.DataArray)
    assert len(os.listdir(tmpdir)) == 1


# test loading local file for get_coverage_data()
@pytest.mark.filterwarnings("ignore:numpy.ufunc size")
def test_load_localfile(tmpdir):
    DbSeabed().get_data(
        "carbonate",
        west=-66.8,
        south=18.0,
        east=-66.2,
        north=18.4,
        output=os.path.join(tmpdir, "test.tif"),
    )
    file1_info = os.path.getmtime(os.path.join(tmpdir, "test.tif"))
    assert len(os.listdir(tmpdir)) == 1

    DbSeabed().get_data(
        "carbonate",
        west=-66.8,
        south=18.0,
        east=-66.2,
        north=18.4,
        output=os.path.join(tmpdir, "test.tif"),
        local_file=True,
    )
    file2_info = os.path.getmtime(os.path.join(tmpdir, "test.tif"))

    assert file1_info == file2_info
