"""Unit test package for xweights.
Test if all necessary modules are available"""

import importlib

import pytest


def _importskip(modname):
    try:
        importlib.import_module(modname)
        has = True
    except ImportError:
        has = False
    func = pytest.mark.skipif(not has, reason=f"requires {modname}")
    return has, func


has_dask, requires_dask = _importskip("dask")
has_geopandas, requires_geopandas = _importskip("geopandas")
has_intake, requires_intake = _importskip("intake")
has_numpy, requires_numpy = _importskip("numpy")
has_xarray, requires_xarray = _importskip("xarray")
has_cordex, requires_cordex = _importskip("cordex")
has_xesmf, requires_xesmf = _importskip("xesmf")
