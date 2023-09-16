# flake8: noqa

import pytest
import xarray as xr

import xweights as xw

from . import has_numpy  # noqa
from . import has_xarray  # noqa
from . import has_xesmf  # noqa
from . import requires_numpy  # noqa
from . import requires_xarray  # noqa
from . import requires_xesmf  # noqa


def test_spatial_averager():
    netcdffile = xw.test_netcdf[0]
    shp = xw.get_region("states")
    ds = xr.open_dataset(netcdffile)
    assert xw.spatial_averaging(ds, shp)
