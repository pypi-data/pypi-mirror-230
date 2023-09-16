import xarray as xr
import xesmf as xe


def get_spatial_averager(ds, gdf, name=None):
    """get xesmf's spatial averager

    Parameters
    ----------
    ds: xr.Dataset

    gdf:
        gp.GeoDataFrame
    name: str (optional)
        `gdf`'s column name

    Returns
    -------
    savg - xesmf.SpatialAverager
    """
    savg = xe.SpatialAverager(ds, gdf.geometry)
    if name is None:
        name = gdf.attrs["name"]
    savg.name = name
    savg.field_region = gdf[name]
    return savg


def spatial_averaging(ds, gdf=None, savg=None):
    """xesmf's spatial averager

    Parameters
    ----------
    ds: xr.Dataset

    gdf: gp.GeoDataFrame (optional)

    savg: xesmf.SpatialAverager (optional)

    Returns
    -------
    out - xr.Dataset
        Dataset containing a time series of spatial averages
        for each geometry in ``gdf``

    Example
    -------
    To create a time series of spatial averages::

        import xweights as xw
        import xarray as xr

        ncf = (
            "tas_EUR-11_MIROC-MIROC5_rcp85_r1i1p1_"
            "CLMcom-CCLM4-8-17_v1_mon_200601-201012.nc"
        )

        ds = xr.open_dataset(ncf)

        shp = xw.get_region('states')

        out = xw.spatial_averager(ds, gdf)

    """
    if savg is None:
        savg = get_spatial_averager(ds, gdf)
    elif isinstance(savg, str):
        savg = get_spatial_averager(savg, gdf)

    nnz = [w.data.nnz for w in savg.weights]
    out = savg(ds)
    dims = ("geom",)
    out = out.assign_coords(
        {
            savg.name: xr.DataArray(
                savg.field_region,
                dims=dims,
            ),
            "nnz": xr.DataArray(
                nnz,
                dims=dims,
            ),
        },
    )
    return out
