# -*- coding: utf-8 -*-
# flake8: noqa

import pytest

import xweights as xw

from . import has_dask, has_intake, requires_dask, requires_intake


def test_get_dataset_dict():
    netcdffile = xw.test_netcdf[0]
    assert xw.Input(netcdffile).dataset_dict
