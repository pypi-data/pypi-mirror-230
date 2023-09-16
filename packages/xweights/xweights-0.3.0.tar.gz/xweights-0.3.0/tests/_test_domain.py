# -*- coding: utf-8 -*-
# flake8: noqa

import pytest

import xweights as xw

from . import has_cordex, requires_cordex


def test_which_domains():
    assert xw.which_domains()


def test_get_domain():
    assert xw.get_domain("EUR-11")
