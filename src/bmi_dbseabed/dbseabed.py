from __future__ import annotations

import os

import rioxarray


class DbSeabed:
    # TODO update bmi names
    DATA_SERVICES = {
        "carbonate": {
            "name": "surficial_seafloor_carbonate__fraction",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_crb_idw3d.tif",
            "units": "percent",
        },
        "carbonate_totlsu": {
            "name": "surficial_seafloor_carbonate__fraction_uncertainty",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_crb_idw3d_TotlSU.tif",
            "units": "percent",
        },
        "grainsize": {
            "name": "surficial_seafloor_sediment__grain-size",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_grz_idw3d.tif",
            "units": "phi",
        },
        "grainsize_totlsu": {
            "name": "surficial_seafloor_sediment__grain-size_uncertainty",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_grz_idw3d_TotlSU.tif",
            "units": "phi",
        },
        "gravel": {
            "name": "surficial_seafloor_sediment_gravel__fraction",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_codaGVL_idw3d.tif",
            "units": "percent",
        },
        "gravel_totlsu": {
            "name": "surficial_seafloor_sediment_gravel__fraction_uncertainty",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_codaGVL_TotlSU.tif",
            "units": "percent",
        },
        "mud": {
            "name": "surficial_seafloor_sediment_mud__fraction",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_codaMUD_idw3d.tif",
            "units": "percent",
        },
        "mud_totlsu": {
            "name": "surficial_seafloor_sediment_mud__fraction_uncertainty",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_codaMUD_TotlSU.tif",
            "units": "percent",
        },
        "organic_carbon": {
            "name": "surficial_seafloor_sediment_organic-carbon__fraction",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_ocbn_idw3d.tif",
            "units": "percent",
        },
        "organic_carbon_totlsu": {
            "name": "surficial_seafloor_sediment_organic-carbon__fraction_uncertainty",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_ocbn_idw3d_TotlSU.tif",
            "units": "percent",
        },
        "rock": {
            "name": "surficial_seafloor_rock~exposed__fraction",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_rck_idw3d.tif",
            "units": "percent",
        },
        "rock_totlsu": {
            "name": "surficial_seafloor_rock~exposed__fraction_uncertainty",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_rck_idw3d_TotlSU.tif",
            "units": "percent",
        },
        "sand": {
            "name": "surficial_seafloor_sediment_sand__fraction",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_codaSND_idw3d.tif",
            "units": "percent",
        },
        "sand_totlsu": {
            "name": "surficial_seafloor_sediment_sand__fraction_uncertainty",
            "link": "https://csdms.colorado.edu/pub/data/dbSEABED/gomex_codaSND_TotlSU.tif",
            "units": "percent",
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
        # Print data services information
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
        """
        Get data from the remote server.

        Args:
            var_name: Variable name for dbSEABED datasets.
            west: x coordinate of the lower left corner of the grid extent.
            south: y coordinate of the lower left corner of the grid extent.
            east: x coordinate of the upper right corner of the grid extent.
            north: y coordinate of the upper right corner of the grid extent.
            output: Output file path.
            local_file: If True, load the local file without data download.

        Returns:
            rioxarray.Dataset: Dataset containing the dbSEABED dataset.
        """

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
        if not output.endswith(".tif"):
            raise ValueError(
                "Please provide a valid output file name with .tif extension."
            )

        if local_file and os.path.isfile(output):
            # load local data
            dataset = rioxarray.open_rasterio(output, masked=True)

        else:
            # access and subset data from server
            ori_data = rioxarray.open_rasterio(
                DbSeabed.DATA_SERVICES[var_name]["link"], masked=True
            )
            dataset = ori_data.rio.clip_box(
                minx=west,
                miny=south,
                maxx=east,
                maxy=north,
            )

            # save the data as geotiff
            dataset.rio.to_raster(
                raster_path=output,
                driver="GTiff",
                recalc_transform=False,
            )

        # get resolution
        geotrans = [
            float(value)
            for value in dataset["spatial_ref"].attrs["GeoTransform"].split(" ")
        ]
        grid_res = [round(abs(geotrans[1]), 8), round(abs(geotrans[5]), 8)]

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
            "node_bounding_box": [
                round(dataset.x.values[0], 8),
                round(dataset.y.values[0], 8),
                round(dataset.x.values[-1], 8),
                round(dataset.y.values[-1], 8),
            ],
            "grid_bounding_box": [round(value, 8) for value in dataset.rio.bounds()],
            "grid_res": grid_res,
        }

        return dataset
