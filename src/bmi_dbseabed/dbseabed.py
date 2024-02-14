from __future__ import annotations

import os

import rioxarray


class DbSeabed:
    # TODO update the dict to add correct bmi names and links and units
    DATA_SERVICES = {
        "bathy": {
            "name": "ocean_bathymetry ",
            "link": "https://",
            "units": "meter",
        },
        "carbonate": {
            "name": "ocean_carbonate",
            "link": "https://files.isric.org/soilgrids/former/"
            "2017-03-10/data/BDRICM_M_250m_ll.tif",
            "units": "%",
        },
        "grainsize": {
            "name": "grain_size",
            "link": "https://",
            "units": "",
        },
        "gravel": {
            "name": "gravel_content",
            "link": "https://",
            "units": "%",
        },
        "mud": {
            "name": "mud_content",
            "link": "https://",
            "units": "%",
        },
        "organic_carbon": {
            "name": "organic_carbon_content",
            "link": "https://",
            "units": "%",
        },
        "rock": {
            "name": "rock_content",
            "link": "https://",
            "units": "%",
        },
        "sand": {
            "name": "sand_content",
            "link": "https://",
            "units": "%",
        },
    }

    def __init__(self):
        self._tif_file = None
        self._metadata = None

    @property
    def tif_file(self):
        return self._tif_file

    @property
    def metadata(self):
        return self._metadata

    @property
    def data_services(self):
        string_list = []
        for key, value in DbSeabed.DATA_SERVICES.items():
            string_list.extend(
                [
                    f"Variable name: {key}",
                    f"Variable units: {value['units']}",
                    f"BMI standard name: {value['name']}",
                    f"Data link: {value['link']}\n",
                ]
            )
        print(os.linesep.join(string_list))

    def get_data(
        self,
        var_name,
        west,
        south,
        east,
        north,
        output,
        local_file=False,
    ):
        # TODO: add docstrings
        # check var_name
        if var_name not in DbSeabed.DATA_SERVICES.keys():
            raise ValueError("Please provide a valid var_name value.")

        # check bounding box
        if west > east or south > north:
            raise ValueError(
                "Please provide valid bounding box values for west, east, south and"
                " north."
            )

        # check output
        if output[-4::] != ".tif":
            raise ValueError(
                "Please provide a valid output file name with .tif extension."
            )

        if local_file and os.path.isfile(output):
            # load local data
            dataset = rioxarray.open_rasterio(output)

        else:
            # access and subset data from server
            ori_data = rioxarray.open_rasterio(DbSeabed.DATA_SERVICES[var_name]["link"])
            dataset = ori_data.rio.clip_box(
                minx=west,
                miny=south,
                maxx=east,
                maxy=north,
            )

            # save the data as geotiff
            dataset.rio.to_raster(raster_path=output, driver="GTiff")

        dataset.close()

        # get resolution
        geotrans = [
            float(value)
            for value in dataset["spatial_ref"].attrs["GeoTransform"].split(" ")
        ]
        grid_res = [abs(geotrans[1]), abs(geotrans[5])]

        # get crs
        crs_wkt = dataset["spatial_ref"].attrs["spatial_ref"]

        # store metadata
        self._tif_file = (
            output
            if os.path.dirname(output) != ""
            else os.path.join(os.getcwd(), output)
        )
        self._metadata = {
            "variable_name": var_name,
            "bmi_standard_name": DbSeabed.DATA_SERVICES[var_name]["name"],
            "variable_units": DbSeabed.DATA_SERVICES[var_name]["units"],
            "service_url": DbSeabed.DATA_SERVICES[var_name]["link"],
            "crs_wkt": crs_wkt,
            "bounding_box": [west, north, east, south],
            "grid_res": grid_res,
        }

        return dataset
