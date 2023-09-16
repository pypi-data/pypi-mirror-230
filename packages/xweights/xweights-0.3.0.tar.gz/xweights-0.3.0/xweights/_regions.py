import os

import cordex as cx
import geopandas as gp
import pandas as pd

from ._geometry import convert_crs, merge_entries


def _pooch_retrieve(url, known_hash=None):
    from pooch import retrieve

    cache_url = "~/.xweights"
    return retrieve(
        url=url,
        path=cache_url,
        known_hash=known_hash,
    )


def _get_geodataframe(shape, name="name"):
    import geopandas as gpd

    gdf = gpd.read_file(shape)
    gdf.attrs["name"] = name
    return gdf


class Regions:
    """The class `Regions` provides gp.GeoDataFrames of pre-defined regions.
    In addition, you can create a new region gp.GeoDataFrame by specifying
    a shapefile on disk.

    **Attributes:**
        *regions:* list
            List of pre-defined regions (from py-cordex)
        *counties:* class
            Containing information about Landkreise in Germany
        *counties_merged:* class
            Containing information about Landkreise in Germany
            (merged if less than 400m^2)
        *states:* class
            Containing information about Bundeslaender in Germany
        *prudence:* class
            Containing information about PRUDENCE regions
        *ipcc:* class
            containing AR6-IPCC-WGI Reference Regions v4 from the Atlas
        *userreg*: class
            Containing information about user-given shapefile
    """

    def __init__(self, geodataframe=None, selection=None):
        self.regions = [
            "counties",
            "counties_merged",
            "states",
            "prudence",
            "ipcc",
        ]
        self.counties = self.Counties()
        self.counties_merged = self.Counties_merged()
        self.states = self.States()
        self.prudence = self.Prudence()
        self.ipcc = self.IPCC()
        self.userreg = self.UserRegion(geodataframe, selection)

    def get_region_names(self, regionname):
        regionname = getattr(self, regionname)
        geodataframe = regionname.geodataframe
        regionsel = regionname.selection
        return list(getattr(geodataframe, regionsel))

    def get_description(self, regionname):
        regionname = getattr(self, regionname)
        return regionname.description

    def get_subset(self, regionname, subset):
        regionname = getattr(self, regionname)
        geodataframe = regionname.geodataframe
        regionsel = regionname.selection
        if isinstance(subset, str):
            subset = [subset]
        return geodataframe[geodataframe[regionsel].isin(subset)]

    class Counties:
        def __init__(self):
            self.description = "Counties (Landkreise) from Germany."
            self.geodataframe = cx.regions.germany.geodataframe("krs")
            self.selection = "name"

    class Counties_merged:
        def __init__(self):
            self.description = (
                "Counties (Landkreise) from Germany (merged less than 400m2)"
            )
            self.geodataframe = self._counties_merged()
            self.selection = "name"

        def _counties_merged(self):
            url_base = (
                "https://github.com/ludwiglierhammer/test_data/raw/main/shp"  # noqa
            )
            url = os.path.join(
                url_base, "NUTS3_merged_counites_less_than_400m2.shape.zip"
            )
            shape_zip = _pooch_retrieve(
                url,
                known_hash="2ca82af334aee2afdcce4799d5cc1ce50ce7bd0710c9ec39e6378519df60ad7a",  # noqa
            )
            return _get_geodataframe(shape_zip, name="NUTS_ID")

    class IPCC:
        def __init__(self):
            self.description = "AR6-IPCC-WGI Ref. Regions v4"
            self.geodataframe = self._ipcc()
            self.selection = "Acronym"

        def _ipcc(self):
            url_base = (
                "https://github.com/ludwiglierhammer/test_data/raw/main/shp"  # noqa
            )
            url = os.path.join(
                url_base, "IPCC-WGI-reference-regions-v4_shapefile.zip"
            )  # noqa
            shape_zip = _pooch_retrieve(
                url,
                known_hash="c83881a18e74912385ad578282de721cc8e866b62cbbc75446e52e7041c81cff",  # noqa
            )
            return _get_geodataframe(shape_zip, name="IPCCv4")

    class States:
        def __init__(self):
            self.description = "States (Bundesländer) from Germany"
            self.geodataframe = cx.regions.germany.geodataframe("lan")
            self.selection = "name"

    class Prudence:
        def __init__(self):
            self.description = "PRUDENCE regions"
            self.geodataframe = cx.regions.prudence.geodataframe
            self.selection = "name"

    class UserRegion:
        def __init__(self, geodataframe, selection):
            self.description = ""
            self.geodataframe = geodataframe
            self.selection = selection


def _region_dict(func, reg):
    return {name: func(name) for name in reg if hasattr(Regions(), name)}


def which_regions():
    """Dictionary containing names of all pre-defined regions

    Returns
    -------
    Dicitonary : dict
        Dictionary containing names of all pre-defined regions
        and their short description
    """
    regions = Regions().regions
    func = Regions().get_description
    return _region_dict(func, regions)


def which_subregions(region):
    """Dictionary containing names of all subregions of one pre-defined region

    Parameters
    ----------
    region: str
        Name of pre-defined region

    Returns
    -------
    Dictionary : dict
        Dictionary containing names of all subgregions
        of one pre-defined region.

    Example
    -------

    To get names of all 'Bundesländer'::

        import xweights as xw

        subregions = xw.which_subregions('states')
    """
    if isinstance(region, str):
        region = [region]
    region = [r.lower() for r in region]
    func = Regions().get_region_names
    return _region_dict(func, region)


def get_region(region_names, name=None, merge=None, column=None):
    """GeoDataFrame containg region information

    Parameters
    ----------
    region_names: str or list
        Pre-defined regions(s) or name of shape file(s)

    name: str or list (optional)
        Name of the sub region(s) to be selected

    merge: str (optional)
        Name of the column to be merged together

    column: str (optional)
        Name of the new column if `merge` is set

    Returns
    -------
    GeoDataFrame : pd.GeoDataFrame
        GeoDataFrame containing region information

    Example
    -------
    To create 'Bundeslander' GeoDataFrame::

        import xweights as xw

        gdf = xw.get_region(states)

    To create subregion 'Hamburg' GeoDataFrame::

        gdf = xw.get_region(states, name='02_Hamburg')

    To create user-defined GeoDataFrame
    and merge all geometries to a single one::

        shpfile = 'Seewinkel.shp'

        gdf = xw.get_region(shpfile, merge='VA')
    """
    gdf = []
    if isinstance(region_names, str):
        region_names = [region_names]
    for region in region_names:
        if os.path.isfile(region):
            if not column:
                raise ValueError("Please set a column name.")
            geodataframe = gp.read_file(region)
            regions = Regions(geodataframe, column)
            region = "userreg"
        elif hasattr(Regions(), region.lower()):
            region = region.lower()
            regions = Regions()
            if column:
                setattr(getattr(regions, region), "selection", column)
            else:
                column = getattr(regions, region).selection
        else:
            raise FileNotFoundError(f"File {region} not available")
        if name:
            gdf += [regions.get_subset(region, name)]
        else:
            gdf += [getattr(regions, region).geodataframe]

    gdf = gp.GeoDataFrame(pd.concat(gdf, ignore_index=True))
    gdf = convert_crs(gdf)
    gdf.attrs["name"] = column
    if merge:
        gdf = merge_entries(gdf, merge)
    return gdf
