# flake8: noqa

import pytest

import xweights as xw

from . import has_cordex, has_geopandas, requires_cordex, requires_geopandas


def test_which_regions():
    assert xw.which_regions()


def test_which_subregions():
    assert xw.which_subregions("counties")
    assert xw.which_subregions("counties_merged")
    assert xw.which_subregions("ipcc")
    assert xw.which_subregions("prudence")
    assert xw.which_subregions("states")


def test_get_region():
    xw.get_region("counties")
    xw.get_region("counties_merged")
    xw.get_region("ipcc")
    xw.get_region("prudence")
    xw.get_region("states")
    xw.get_region("states", name="02_Hamburg")
    xw.get_region("states", name=["01_Schleswig-Holstein", "02_Hamburg"], merge="all")


def test_get_user_region():
    shpfile = xw.test_shp[0]
    xw.get_region(shpfile, merge="VA", column="VA")
