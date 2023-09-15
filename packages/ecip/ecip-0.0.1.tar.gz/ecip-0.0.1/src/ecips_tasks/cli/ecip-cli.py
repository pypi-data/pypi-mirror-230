import pyarrow as pa
import pyarrow.dataset as ds
import numpy as np
import json
import sys
from datetime import datetime, timedelta, date

# transfer results
import os
import shutil

# parse CL args
import argparse

# -- Pull test server detections -- ###

# Import and set fields for pulling table off server

fields = [
    pa.field("year", pa.int16()),
    pa.field("month", pa.int8()),
    pa.field("day", pa.int32()),
    pa.field("img_filepath", pa.string()),
    pa.field("plant_name", pa.string()),
    pa.field("mpe_ip", pa.string()),
    pa.field("num_hazmat_labels", pa.int64()),
    pa.field("hazmat_scores", pa.list_(pa.float64())),
    pa.field("detected_hazmat", pa.list_(pa.float64())),
    pa.field("Hazmat_model_version", pa.string()),
    pa.field("hazmat_classes", pa.list_(pa.float64())),
]


# process results
class NumpyEncoder(json.JSONEncoder):
    """Special json encoder for numpy types"""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def export_hazmat_results(
    days=1, conf_thresh=0.5, export_dir_name="", export_results=False, print_stdout=True
):

    # Pull and process data
    dataset = ds.dataset(
        "/mnt/database/ecips_db/",
        format="parquet",
        partitioning="hive",
        schema=pa.schema(fields),
    )

    search_day = None
    if True:
        if search_day is None:
            search_day = datetime.now() - timedelta(days=days)

    filters = (
        (ds.field("year") == search_day.year)
        & (ds.field("month") == search_day.month)
        & (ds.field("day") == search_day.day)
    )

    # Data Processing
    # convert to pandas
    df_hazmat = dataset.to_table(filter=filters).to_pandas()

    df_hazmat = df_hazmat[~df_hazmat.num_hazmat_labels.isna()]
    # get first score col
    df_hazmat["first_score"] = [x[0] for x in df_hazmat["hazmat_scores"].values]
    df_hazmat["hazmat_classes_first"] = df_hazmat["hazmat_classes"]

    # mapping
    results_list = []
    for x in df_hazmat["hazmat_classes_first"].values:
        if x is None:
            result = 99
        else:
            result = x[0]
        results_list.append(result)

    df_hazmat["hazmat_classes_first"] = results_list

    # Print to console
    results_json = {}
    results_json["Total_records"] = len(df_hazmat)
    results_json["Total_unique_images"] = len(df_hazmat["img_filepath"].unique())
    results_json["Total_hazmat_detections"] = int(df_hazmat["num_hazmat_labels"].sum())
    results_json["Images_with_hazmat"] = len(
        df_hazmat[df_hazmat["num_hazmat_labels"] > 0]
    )
    results_json["Images_with_hazmat_above_conf"] = len(
        df_hazmat[df_hazmat["first_score"] > conf_thresh]["img_filepath"].unique()
    )

    if False:
        print("Total records: ", len(df_hazmat))
        print("Total unique images: ", len(df_hazmat["img_filepath"].unique()))
        print("Total hazmat detections: ", df_hazmat["num_hazmat_labels"].sum())
        print(
            "Total images with at least one hazmat detection, any thresh: ",
            len(df_hazmat[df_hazmat["num_hazmat_labels"] > 0]),
        )
        print(
            "Total images with at least one detection above confidence threshold: ",
            len(
                df_hazmat[df_hazmat["first_score"] > conf_thresh][
                    "img_filepath"
                ].unique()
            ),
        )

    # Get "high" confidence detections aka ones above thresh
    df_hazmat_highconf = df_hazmat[df_hazmat.first_score >= conf_thresh].copy()
    results_json["Images_Hazmat_ValueCount"] = (
        df_hazmat_highconf["hazmat_classes_first"].value_counts().to_dict()
    )

    # Make export dir and export files
    export_dir_path = "{}".format(export_dir_name)  # should change daily
    if export_results:
        os.mkdirs(export_dir_path)
        for img_filepath in df_hazmat_highconf.img_filepath.values:
            shutil.copy(img_filepath, export_dir_path)

        df_hazmat_highconf.to_json(f"{export_dir_name}/result_summary.json")

    json_datasummary = json.dumps(results_json, cls=NumpyEncoder)

    if print_stdout:
        print(json_datasummary, file=sys.stdout)


def parse(args):

    parser = argparse.ArgumentParser(description="ECIP-Application Command Line Tool")
    subparsers = parser.add_subparsers(help="sub-command", dest="command")
    subparsers.required = True
    parser_sum_hz = subparsers.add_parser(
        "summarize-hazmat", help="Manually create JSON"
    )

    parser_sum_hz.add_argument(
        "--days_ago",
        default=0,
        type=int,
        help="""Pull detections from n days ago. 0 is today.""",
    )

    parser_sum_hz.add_argument(
        "--conf_thresh",
        default=0.5,
        type=float,
        help="""Confidence threshold of proposed detections.""",
    )

    parser_sum_hz.add_argument(
        "--export_dir_name",
        default=f'/mnt/database/{date.today().strftime("%Y-%m-%d")}',  # today's date as a string
        type=str,
        help="""Name of directory to export detection images to.""",
    )

    parser_sum_hz.add_argument(
        "--export_images",
        default=False,
        action="store_true",
        help="Select this flag to export results",
    )

    return parser.parse_args(args)


def main(args=None):

    args = parse(args)

    if args.command == "summarize-hazmat":
        export_hazmat_results(
            days=args.days_ago,
            conf_thresh=args.conf_thresh,
            export_dir_name=args.export_dir_name,
            export_results=args.export_images,
        )


if __name__ == "__main__":
    main()
