# flake8: noqa

import pytest
import xarray as xr

import xweights as xw

from . import has_cordex  # noqa
from . import has_dask  # noqa
from . import has_geopandas  # noqa
from . import has_intake  # noqa
from . import has_numpy  # noqa
from . import has_xarray  # noqa
from . import has_xesmf  # noqa
from . import requires_cordex  # noqa
from . import requires_dask  # noqa
from . import requires_geopandas  # noqa
from . import requires_intake  # noqa
from . import requires_numpy  # noqa
from . import requires_xarray  # noqa
from . import requires_xesmf  # noqa


def test_compute_weighted_means_ds_gdf():
    netcdffile = xw.test_netcdf[0]
    gdf = xw.get_region("states")
    ds = xr.open_dataset(netcdffile)
    xw.compute_weighted_means_ds(
        ds,
        gdf=gdf,
        time_range=["2007-01-01", "2007-11-30"],
        column_names=[
            "institute_id",
            "driving_model_id",
            "experiment_id",
            "driving_model_ensemlbe_member",
            "model_id",
            "rcm_version_id",
            "units",
            "standard_name",
            "not_available",
        ],
        output=".",
    )


def test_compute_weighted_means_ds_region():
    netcdffile = xw.test_netcdf[0]
    ds = xr.open_dataset(netcdffile)
    xw.compute_weighted_means_ds(
        ds,
        region="states",
        time_range=["2007-01-01", "2007-11-30"],
        column_names=[
            "institute_id",
            "driving_model_id",
            "experiment_id",
            "driving_model_ensemlbe_member",
            "model_id",
            "rcm_version_id",
            "units",
            "standard_name",
            "not_available",
        ],
        output="test",
    )


def test_compute_weighted_means_region():
    netcdffile = xw.test_netcdf[0]
    ds = xr.open_dataset(netcdffile)
    dataset_dict = {"test_data": ds}
    xw.compute_weighted_means(
        dataset_dict,
        region="states",
        subregion=[
            "01_Schleswig-Holstein",
            "02_Hamburg",
            "03_Niedersachsen",
            "04_Bremen",
        ],
        merge_columns=["all", "NorthSeaCoast"],
        output="test.csv",
    )


def test_compute_weighted_means_gdf():
    netcdffile = xw.test_netcdf[0]
    ds = xr.open_dataset(netcdffile)
    dataset_dict = {"test_data": ds}
    gdf = xw.get_region("states")
    xw.compute_weighted_means(
        dataset_dict,
        gdf=gdf,
        subregion=[
            "01_Schleswig-Holstein",
            "02_Hamburg",
            "03_Niedersachsen",
            "04_Bremen",
        ],
        merge_columns=["all", "NorthSeaCoast"],
    )
