import argparse


def str_to_dict(string):
    k, v = string[1:-1].split(":")
    try:
        v = eval(v)
    except Exception:
        pass
    return {k: v}


def str_to_list(str):
    return str.split(",")


class ParseKwargs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())
        for value in values:
            key, value = value.split("=")
            if ":" in value and value[0] == "{" and value[-1] == "}":
                value = str_to_dict(value)
            elif "," in value:
                value = str_to_list(value)
            getattr(namespace, self.dest)[key] = value


def create_parser():
    """
    You can use grid_weighted_means as an command-line tool.
    Use -h for more information
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_files",
        dest="input_files",
        nargs="+",
        help="List of input files",
    )
    parser.add_argument(
        "-o",
        "--output_directory",
        dest="output_directory",
        nargs="?",
        type=str,
        help="Output directory or output file",
    )
    parser.add_argument(
        "-r",
        "--region",
        dest="region",
        nargs="+",
        type=str,
        help=(
            "Region for geometry weighting only."
            "Choose between counties, states, prudence."
            "Or give a shapefile."
        ),
    )
    parser.add_argument(
        "-s",
        "--subregion",
        dest="subregion",
        nargs="+",
        type=str,
        help="Set names of the subregions",
    )
    parser.add_argument(
        "-t_range",
        "--time_range",
        dest="time_range",
        nargs="+",
        help="Select time range from dataset. Use format yyyy[-mm[-dd]]",
    )
    parser.add_argument(
        "-csv_columns",
        "--csv_column_names",
        dest="csv_column_names",
        nargs="+",
        default=[],
        help=(
            "Set the additional output csv column names read"
            "from the dataset global attributes."
        ),
    )
    parser.add_argument(
        "-merge",
        "-merge_columns",
        dest="merge_columns",
        nargs="?",
        type=str,
        help="Column names of shapefile to merge together.",
    )
    parser.add_argument(
        "-column",
        "-column_merge",
        dest="column_merge",
        nargs="?",
        type=str,
        help="Column name to differentiate shapefile while merging.",
    )
    parser.add_argument(
        "-tstat",
        "--time_statistics",
        dest="time_statistics",
        nargs="+",
        help="Set additional statistics over time.",
    )
    parser.add_argument(
        "-lony",
        "--land_only",
        dest="land_only",
        nargs="+",
        help="Consider only land points.",
    )
    parser.add_argument(
        "-kwargs",
        "--kwargs",
        dest="kwargs",
        nargs="*",
        default={},
        action=ParseKwargs,
        help="User-given dictionary with additional settings.",
    )
    parser.add_argument(
        "-which_regions",
        "--which_regions",
        dest="which_regions",
        nargs="?",
        const=True,
        help="Print available regions on screen.",
    )
    parser.add_argument(
        "-which_subregions",
        "--which_subregions",
        dest="which_subregions",
        nargs="+",
        help="Print all subregions of selected region on screen.",
    )
    return parser


parser = create_parser()
args = parser.parse_args()

if args.merge_columns:
    args.column_merge = args.merge_columns
