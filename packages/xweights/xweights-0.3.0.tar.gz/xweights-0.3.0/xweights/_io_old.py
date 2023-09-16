import glob
import os
import warnings

import dask
import intake
from pyhomogenize import get_var_name, open_xrdataset


def adjust_name(string):
    """Delete special character from string and replace umlauts.
    If string is a directory path: Replace slashes with underscores
    If string is a netCDF file name: Delete directory path and suffix

    Parameters
    ----------
    string: str

    Returns
    -------
    str

    Example
    -------
    Adjust name of string:

        import os
        import xweights as xw

        string = ("/work/kd0956/CORDEX/data/cordex/output/EUR-11/CLMcom/"
                 "MIROC-MIROC5/rcp85/r1i1p1/CLMcom-CCLM4-8-17/v1/mon/tas/"
                 "v20171121/tas_EUR-11_MIROC-MIROC5_rcp85_r1i1p1_"
                 "CLMcom-CCLM4-8-17_v1_mon_200601-201012.nc")

        new_string = xw.adjust_name(string)

        tas_EUR-11_MIROC-MIROC5_rcp85_r1i1p1_CLMcom-CCLM4-8-17_v1_mon_200601-201012

    """
    string = string.replace(" ", "-")
    string = string.replace("(", "")
    string = string.replace(")", "")
    string = string.replace("ä", "ae")
    string = string.replace("ö", "oe")
    string = string.replace("ü", "ue")
    string = string.replace("ß", "ss")
    if ".nc" in string:
        return string.split("/")[-1].split(".nc")[0]
    elif "/" in string:
        return "_".join(string.split("/"))[1:]
    else:
        return string


def create_newname(vars, name):
    """Create new name for string

    Parameters
    ----------
    vars: list
        List of CF variables
    name: str

    Returns
    -------
    str
    """

    def newname(name, var):
        if var not in name:
            name = "{}.{}".format(var, name)
        return name

    return adjust_name([newname(name, var) for var in vars][0])


class Input:
    """The :class:`Input` creates a dataset dictionary
    containing all given input files.
    dataset_dict = {name_of_xrDataset : xrDataset}
    Valid input files are netCDF file(s), directories containing
    those files and intake-esm catalogue files

    **Attributes:**
        *dataset_dict:*
            dictionary

    Example
    -------
       To create a xarray dataset dictionary from intake-esm catalogue file
       using some extra filter options::

           import xweights as xw

           catfile = '/work/kd0956/Catalogs/mistral-cordex.json'

           dataset_dict = xw.Input(
                             catfile,
                             variable_id=tas,
                             experiment_id=rcp85,
                             table_id=mon,
                          )

       To create a xarray dataset dictionary from netCDF file on disk::

           import xweights as xw

           netcdffile = ("/work/kd0956/CORDEX/data/cordex/output/EUR-11/"
                        "CLMcom/MIROC-MIROC5/rcp85/r1i1p1/CLMcom-CCLM4-8-17/"
                        "v1/mon/tas/v20171121/tas_EUR-11_MIROC-MIROC5_rcp85_"
                        "r1i1p1_CLMcom-CCLM4-8-17_v1_mon_200601-201012.nc")

           dataset_dict = xw.Input(netcdffile).dataset_dict

    """

    def __init__(self, input, **kwargs):
        self.dataset_dict = self.create_dataset_dict(input, **kwargs)

    def open_intake_esm_catalogue(self, catfile, **kwargs):
        """Function to open an intake-sm catalogue"""
        cat = intake.open_esm_datastore(catfile)
        if kwargs:
            cat = cat.search(**kwargs)
        with dask.config.set(**{"array.slicing.split_large_chuncks": False}):
            return cat.to_dataset_dict(
                cdf_kwargs={
                    "use_cftime": True,
                    "decode_timedelta": False,
                    "chunks": {},
                }
            )

    def create_input_dictionary(self, input, **kwargs):
        """Function to create xarray dataset dictionary from input"""

        def _create_filelist(input_lst):
            file_lst = []
            for ifile in input:
                if os.path.isfile(ifile):
                    file_lst.append(ifile)
                elif os.path.isdir(ifile):
                    file_lst += glob.glob(ifile + "/*")
                else:
                    warnings.warn(
                        "Could not find input file(s) {}.".format(
                            ifile,
                        )
                    )
            return file_lst

        def _get_input_dict(iname, ifiles, **kwargs):
            inputdict = {}
            try:
                print(ifiles)
                inputdict[iname] = open_xrdataset(ifiles, **kwargs)
                print(inputdict[iname].chunks)
                exit()
                return inputdict
            except Exception:
                pass

            for ifile in ifiles:
                try:
                    inputdict[ifile] = open_xrdataset(ifile, **kwargs)
                    continue
                except Exception:
                    pass
                try:
                    inputdict.update(
                        self.open_intake_esm_catalogue(ifile, **kwargs),
                    )
                    continue
                except Exception:
                    warnings.warn(
                        "Input file {} has no valid file format."
                        "Use netCDF files or"
                        "intake-esm catalogues.".format(ifile)
                    )
            return inputdict

        files = _create_filelist(input)

        return _get_input_dict(input[0], files, **kwargs)

    def identify_input_format(self, input, **kwargs):
        """Function to identify input file format"""
        if isinstance(input, str):
            input = [input]
        if isinstance(input, list):
            inputdict = self.create_input_dictionary(input, **kwargs)
        if isinstance(input, dict):
            inputdict = input
        return inputdict

    def create_dataset_dict(self, input, **kwargs):
        """Returns xarray dataset dictionary"""
        inputdict = self.identify_input_format(input, **kwargs)
        if not inputdict:
            raise IndexError("Empty file dictionary")
        for name, ds in inputdict.items():
            ds.attrs["vars"] = get_var_name(ds)
            inputdict[name] = ds
        return {
            create_newname(
                ds.vars,
                name,
            ): ds
            for name, ds in inputdict.items()
        }
