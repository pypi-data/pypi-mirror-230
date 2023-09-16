import pandas as pd
import xarray as xr

from ._regions import get_region
from ._tabulator import concat_dataframe, write_to_csv
from ._weightings import get_spatial_averager, spatial_averaging


def _get_gdf(gdf=None, region=None, subregion=None, merge=None, column=None):
    if gdf is None:
        return get_region(
            region,
            name=subregion,
            merge=merge,
            column=column,
        )
    return gdf


def _get_averager(
    averager=None,
    ds=None,
    gdf=None,
):
    if averager is True:
        return get_spatial_averager(
            ds,
            gdf,
        )
    return averager


def compute_weighted_means_ds(
    ds,
    ds_name="dataset",
    region=None,
    subregion=None,
    gdf=None,
    averager=True,
    time_range=None,
    column_names=[],
    merge_columns=False,
    column_merge=False,
    df_output=pd.DataFrame(),
    output=None,
    land_only=False,
    time_stat=False,
):
    """
    Compute spatial weighted mean of xr.Dataset

    Parameters
    ----------
    ds: xr.Dataset

    ds_name: str (optional)
        Name of the dataset will be written to the pd.DataFrame
        as an extra column.

    region: str (optional)
        Name of the shapefile or pre-defined region
        containing the information needed
        for xesmf's spatial averaging.

    subregion: str or list (optional)
        Name of the subregion(s) to be selected from ``region``

    gdf: gp.GeoDataFrame (optional)
       gp.GeoDataFrame containing the information needed
       for xesmf's spatial averaging.

    averager: bool or xesmf.SpatialAverager (optional)
        If True: Calculate a xesmf.SpatialAverager
        Else: Use user-given xesmf.SpatialAverager

    time_range: list (optional)
        List containing start and end date to select from ``ds``

    column_names: list (optional)
        Extra column names of the pd.DataFrame;
        the information is read from both global attributes
        and variable attributes from `ds`.

    merge_columns: str or list (optional)
        Name of the column to be merged together.
        Set ['all', 'newname'] to merge all geometries
        and set new column name to 'newname'.

    column_merge: str (optional)
        Column name to differentiate shapefile while merging.

    df_output: pd.DataFrame (optional)
        pd.DataFrame to be concatenated with the newly created pd.DataFrame

    output: str (optional)
        Name of the output directory path or file

    land_only: bool (optional)
        Consider only land points\n
        !!!This is NOT implemented yet!!!\n
        As workaround write land sea mask in ``ds['mask']``.
        xesmf's spatial averager automatically considers ``ds['mask']``.

    time_stat: str or list (optional)
       Do some time statistics on ``ds``\n
       !!!This is NOT implemented yet!!!

    Returns
    -------
    DataFrame : pd.DataFrame
        pandas Dataframe containing time series of spatial averages.


    Example
    -------

    To calculate time series of spatial averages for several 'Bundelaender':\n
        - select Schleswig-Holstein, Hamburg, Bremen and Lower Saxony\n
        - Merge those regions to one new region calles NortSeaCoast\n
        - Select time slice from 2007 to 2009\n
        - Set CORDEX specific result DataFrame column names\n
    ::

        import xarray as xr
        import xweights as xw

        ncf = (
            "/tas_EUR-11_MIROC-MIROC5_rcp85_r1i1p1_"
            "CLMcom-CCLM4-8-17_v1_mon_200601-201012.nc"
        )

        ds = xr.open_dataset(ncf)
        df = xw.compute_weighted_means_ds(ds,
                                          region="states",
                                          subregions=["01_Schleswig-Holstein",
                                                      "02_Hamburg",
                                                      "03_Niedersachsen",
                                                      "04_Bremen"],
                                          merge_column=["all",
                                                       "NorthSeaCoast"],
                                          time_range=["2007-01-01","2009-12-31"],
                                          column_names=["institute_id",
                                                        "driving_model_id",
                                                        "experiment_id",
                                                        "driving_model_ensemble_member",
                                                        "model_id",
                                                        "rcm_version_id"],
                                          )
    """
    if land_only:
        """
        Not clear how to find right lsm file for each ds
        Then write lsm file to ds['mask']
        The rest is done by xesmf
        """
        NotImplementedError

    if not isinstance(ds, xr.Dataset):
        return df_output

    if time_range:
        ds = ds.sel(time=slice(time_range[0], time_range[1]))

    gdf = _get_gdf(
        gdf=gdf,
        region=region,
        subregion=subregion,
        merge=merge_columns,
        column=column_merge,
    )

    averager = _get_averager(
        averager=averager,
        ds=ds,
        gdf=gdf,
    )

    out = spatial_averaging(ds, gdf, savg=averager)
    drop = [i for i in out.coords if not out[i].dims]
    out = out.drop(labels=drop)

    column_dict = {}
    for column in column_names:
        skip = False
        if hasattr(ds, column):
            column_dict[column] = ds.attrs[column]
            continue
        for data_var in out.data_vars:
            if hasattr(ds[data_var], column):
                skip = True
                value = ds[data_var].attrs[column]
                if data_var in column_dict.keys():
                    column_dict[data_var][column] = value
                else:
                    column_dict[data_var] = {column: value}
        if skip is False:
            column_dict[column] = None

    if time_stat:
        """
        Not sure if it is usefull to implement here or
        do it seperately after using xweights.
        """
        NotImplementedError
    df_output = concat_dataframe(
        df_output,
        out,
        column_dict=column_dict,
        name=ds_name,
    )

    if output:
        write_to_csv(df_output, output)
    return df_output


def compute_weighted_means(
    dataset_dict,
    region=None,
    subregion=None,
    gdf=None,
    averager=False,
    averager_ds=None,
    time_range=None,
    column_names=[],
    merge_columns=False,
    column_merge=False,
    output=None,
    land_only=False,
    time_stat=False,
    **kwargs
):
    """
    Compute spatial weighted mean of user-given inputs.


    Parameters
    ----------
    dataset_dict: dict
        Input dictionary.
        Key: xr.dataset name
        Value: xr.Dataset

    region: str (optional)
        Name of the shapefile or pre-defined region
        containing the information needed
        for xesmf's spatial averaging.

    subregion: str or list (optional)
        Name of the subregion(s) to be selected from ``region``

    gdf: gp.GeoDataFrame (optional)
        gp.GeoDataFrame containing the information
        needed for xesmf's spatial averaging

    averager: bool or xesmf.SpatialAverager object (optional)
        If True: Calculate one xesmf.SpatialAverager to use for all datasets.
        `ds_averager` is needed.
        If False or None: Calculate a xesmf.SpatialAverager
        individually for each ds.
        Else use user-given xesmf.SpatialAverager

    averager_ds: xr.Dataset
        If `averager` is True use for calculating one xesmf.SpatialAverager
        to use for all dataset.

    time_range: list (optional)
        List containing start and end date to be select

    column_names: list (optional)
        Extra column names of the pd.DataFrame;
        the information is read from global attributes

    merge_columns: str or list (optional)
        Name of the column to be merged together.
        Set ['all', 'newname'] to merge all geometries
        and set new column name to 'newname'.

    column_merge: str (optional)
        Column name to differentiate shapefile while merging.

    outdput: str (optional)
        Name of the output directory path or file

    land_only: bool (optional)
        Consider only land points\n
        !!!This is NOT implemented yet!!!\n
        As workaround write land sea mask in ``ds['mask']``.
        xesmf's spatial averager automatically considers ``ds['mask']``.

    time_stat: str or list (optional)
       Do some time statistics on ``ds``\n
       !!!This is NOT implemented yet!!!

    Returns
    -------
    DataFrame : pd.DataFrame
        pandas Dataframe containing time series of spatial averages.

    Example
    -------

    To calculate time series of spatial averages for several 'Bundelaender':\n
        - select Schleswig-Holstein, Hamburg, Bremen and Lower Saxony\n
        - Merge those regions to one new region calles NortSeaCoast\n
        - Select time slice from 2007 to 2009\n
        - Set CORDEX specific result DataFrame column names\n
    ::

        import xweights as xw
        import xarray as xr

        nc = (
            "tas_EUR-11_MIROC-MIROC5_rcp85_r1i1p1_"
            "CLMcom-CCLM4-8-17_v1_mon_200601-201012.nc"
        )

        ds = xr.open_dataset(nc)
        dataset_dict = {
            "EUR-11_MIROC-MIROC5_rcp85_r1i1p1_CLMcom-CCLM4-8-17_v1_mon": ds,
        }

        df = xw.compute_weighted_means_ds(dataset_dict,
                                          'states',
                                          subregions=['01_Schleswig-Holstein,
                                                      '02_Hamburg',
                                                      '03_Niedersachsen',
                                                      '04_Bremen'],
                                          merge_column=['all',
                                                       'NorthSeaCoast'],
                                          time_range=['2007-01-01','2009-12-31'],
                                          column_names=['institute_id',
                                                        'driving_model_id',
                                                        'experiment_id',
                                                        'driving_model_ensemlbe_member',
                                                        'model_id',
                                                        'rcm_version_id'],
                                          )


    """

    def _calc_time_statistics(ds, statistics):
        return ds

    gdf = _get_gdf(
        gdf=gdf,
        region=region,
        subregion=subregion,
        merge=merge_columns,
        column=column_merge,
    )

    averager = _get_averager(
        averager=averager,
        ds=averager_ds,
        gdf=gdf,
    )
    if isinstance(averager, bool):
        averager = True

    df_output = pd.DataFrame()
    for name, ds in dataset_dict.items():
        df_output = compute_weighted_means_ds(
            ds,
            gdf=gdf,
            ds_name=name,
            time_range=time_range,
            column_names=column_names,
            averager=averager,
            df_output=df_output,
            land_only=land_only,
            time_stat=time_stat,
        )

    if output:
        write_to_csv(df_output, output)

    return df_output
