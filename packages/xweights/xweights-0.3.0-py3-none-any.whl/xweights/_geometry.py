import geopandas as gp
import pandas as pd
from shapely.ops import unary_union


def convert_crs(gdf, epsg=4326):
    """Transform geometries to a new coordinate reference system.

    Parameters
    ----------
    gdf: gp.GeoDataFrame
        Geopandas GeoDataFrame
    epsg: int
        EPSG code sprecifying output preojection
        Default: 4326

    Returns
    -------
    gp.GeoDataFrame
    """
    return gdf.to_crs(epsg=epsg)


def convert_multipolygon_to_polygon(list_of_polygons):
    """Returns the union of a sequence of geometries

    Parameters
    ----------
    list_of_polygons: list
        List containing geometries

    Returns
    -------
    Singel geometry
    """

    return unary_union(list_of_polygons)


def merge_entries(gdf, column):
    """Merge entries of a GeoDataFrame

    Parameters
    ----------
    gdf: gp.GeoDataFrame
        Geopandas GeoDataFrame
    column: str
        Name of the column which to merge

    Returns
    -------
    gp.GeoDataFrame

    """

    def get_polygeometry(gdf):
        list_of_polygons = [geometry for geometry in gdf.geometry]
        return [convert_multipolygon_to_polygon(list_of_polygons)]

    if isinstance(column, list):
        column, name = column
    else:
        name = "all"

    if column == "all":
        dic = {column: [name]}
        polygeometry = get_polygeometry(gdf)
    else:
        dic = {column: getattr(gdf, column).unique()}
        polygeometry = []
        for values in dic.values():
            for value in values:
                polygeometry += get_polygeometry(
                    gdf[getattr(gdf, column) == value],
                )
    dic["geometry"] = polygeometry
    df = pd.DataFrame(dic)
    gdf = gp.GeoDataFrame(df, geometry="geometry", crs=gdf.crs)
    gdf.attrs["name"] = column
    return gdf
