"""Console script for xweights."""
import sys

from dask.distributed import Client

from ._parser import args
from ._regions import which_regions, which_subregions
from .xweights import compute_weighted_means


def main():
    """Console script for xweights."""
    if args.which_regions:
        print(which_regions())
        return
    if args.which_subregions:
        print(which_subregions(args.which_subregions))
        return
    if not args.input_files:
        raise TypeError(
            "Please select an input file with the option -i."
            "You can choose between netCDF file(s),"
            "directories containing those files"
            "and intake-esm catalogue files."
        )
    if not args.region:
        raise TypeError(
            "Please select a pre-definded region"
            "or a user-given shapefile with the option -r."
            "Use -which_regions to show pre-defined regions"
            "and use -which_subregions <region_name>"
            "to show subregions of specified pre-defined region."
        )

    return compute_weighted_means(
        args.input_files,
        region=args.region,
        subregion=args.subregion,
        time_range=args.time_range,
        column_names=args.csv_column_names,
        merge_columns=args.merge_columns,
        column_merge=args.column_merge,
        outdir=args.output_directory,
        time_stat=args.time_statistics,
        land_only=args.land_only,
        **args.kwargs,
    )


if __name__ == "__main__":
    with Client() as client:
        sys.exit(main())
