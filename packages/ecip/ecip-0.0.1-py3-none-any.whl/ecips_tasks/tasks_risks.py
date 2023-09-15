import os
import glob
import json
import time
import redis
import logging
import numpy as np
import pandas as pd
import pyarrow as pa
from pyarrow import dataset as ds
from celery import Celery
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from ecips_utils import ecips_config, ecips_path
from ecips_tasks import tasks_beats, tasks_faissnv_v1
import tempfile
import orjson


# Create Celery `App` for Tasking
app = Celery(
    "tasks_risks",
    broker=ecips_config.CELERY_BROKER,
    backend=ecips_config.CELERY_BACKEND,
)
app.conf.result_expires = 3 * 60 * 60
app.tasks.register(tasks_beats.risks_health_check)

# Database configs
META = ecips_config.ECIPS_DASK_META_DATA
ECIPS_DATABASE = ecips_config.REVERSE_IMAGE_DB_PATH


# Model configs
def check_float(variable_name):
    if not isinstance(variable_name, float):
        try:
            variable_name = float(variable_name)
        except ValueError:
            logging.info(f"{str(variable_name)} is not convertible to float!")
    return variable_name


APBS_HEADER_SIZE = ecips_config.ECIPS_PRLM_HEADER_SIZE
STAMP_THRESHOLD = check_float(ecips_config.ECIPS_STAMP_RISK_THRESHOLD)
PVI_THRESHOLD = check_float(ecips_config.ECIPS_PVI_RISK_THRESHOLD)
RISK_THRESHOLD = check_float(ecips_config.ECIPS_RISKS_THRES)
IMPORTANT_PACKAGE_CLASS = list(ecips_config.ECIPS_PACKAGE_MAPPINGS.values())[0]
BARCODE_MODEL_WEIGHT = check_float(ecips_config.ECIPS_BARCODE_MODEL_WEIGHT)
STAMP_MODEL_WEIGHT = check_float(ecips_config.ECIPS_STAMP_MODEL_WEIGHT)
PVI_MODEL_WEIGHT = check_float(ecips_config.ECIPS_PVI_MODEL_WEIGHT)
ZIP_MODEL_WEIGHT = check_float(ecips_config.ECIPS_ZIP_MODEL_WEIGHT)
PACKAGE_MODEL_WEIGHT = check_float(ecips_config.ECIPS_PACKAGE_MODEL_WEIGHT)
IMPORTANT_ZIP_LIST = ecips_config.ECIPS_IMPORTANT_ZIPS
SCORE_THRES = check_float(ecips_config.ECIPS_INFERENCE_SCORE_THRES)


# Elastic
ELASTIC_PORT = ecips_config.ELASTIC_PORT
ELASTIC_ENDPOINT = ecips_config.ELASTIC_ENDPOINT
ES = Elasticsearch(ELASTIC_ENDPOINT, scheme="http", port=ELASTIC_PORT)
# System mappings
MPE_MAPPINGS = ecips_config.get_mpe_mappings()
DEVICE_MAPPINGS = ecips_config.ECIPS_DEVICE_MAPPING
HUMAN_READABLE_NAME_MAPPINGS = ecips_config.ECIPS_DEVICE_MAPPING
HUMAN_READABLE_SITE_NAME = ecips_config.ECIPS_SITE_NAME_MAPPING
HUMAN_READABLE_SITE_TYPE = ecips_config.ECIPS_SITE_TYPE_MAPPING
IP = DEVICE_MAPPINGS["ip"]
SITE = HUMAN_READABLE_SITE_NAME[IP]
SITE_TYPE = HUMAN_READABLE_SITE_TYPE[IP]
# Email configs
ECIPS_EMAIL_ALERT_LIST = ecips_config.ECIPS_EMAIL_ALERT_LIST
MAX_EMAIL_SIZE_MB = ecips_config.MAX_EMAIL_SIZE_MB

# Create metadata for DataFrame Transitions into pyarrow
pa_meta = []
new_meta = {}
for key in META.keys():
    if META[key] == "string":
        pa_meta.append((key, pa.string()))
        new_meta[key] = "string"

    elif META[key] == "int64":
        pa_meta.append((key, pa.int64()))
        new_meta[key] = "int64"

    else:
        pa_meta.append((key, pa.float64()))
        new_meta[key] = "float"

schema = pa.schema(pa_meta)

# Identify columns to read from redis and parquet for risk calculation
columns_to_read = [
    "img_filepath",
    "barcode_valid",
    "num_stamps",
    "pvi_scores",
    "package",
    "barcode",
    "mpe_ip",
    "mpe_device",
]


def add_to_index(records):
    """
    This function takes processing results and adds them to an ELK index. Deprecated

    Input:
        results - new processing results
    """
    logging.debug(f"Adding {str(records)} to ELK index.")
    ES.bulk(index="dangerous-mail", body=records)


def check_db(filters):
    """
    This function checks if the database as data for the provided filter range.

    Input:
        filters - filters to read database with the following attributes: year, month , day.
    Output:
        bool
    """
    if glob.glob(
        ECIPS_DATABASE
        + "/**/"
        + f"year={filters.year}/month={filters.month}/day={filters.day}/*"
    ):
        return True
    else:
        return False


def load_ecips_db(search_day, days_reverse=1, columns_to_read=columns_to_read):
    """
    This function loads today and yesterday's data from ecips_db.

    Input:
        search_day - python datetime object for searching ecips_db
        days_reverse - int (default=1) to handle midnight crossover
        columns_to_read - list see ecips_config for defaults, columns to return
    Output:
        search_df - data collected from search_day ecips_db
    """

    logging.debug(f"Attempting to load data from database format: {search_day.isoformat()}")

    search_df = read_ecips_db(search_day, columns_to_read=columns_to_read)

    for daydelta in range(days_reverse):
        search_day_temp = search_day - timedelta(days=daydelta + 1)
        search_df_temp = read_ecips_db(search_day_temp, columns_to_read=columns_to_read)
        search_df = search_df.append(search_df_temp).reset_index(drop=True)

    return search_df


def load_redis(deserialize=False):
    """
    This function loads today data from redis.

    Outputs:
        redis_df - dataframe loaded from redis or bool
    """

    logging.debug("Loading from redis")
    r = redis.Redis(host=ecips_config.CELERY_BACKEND.split(":")[1].replace("//", ""))
    jsonlist = r.lrange("dailyJson_filePath", 0, -1)
    if jsonlist:
        newjsonlist = list(set([ele.decode("utf-8") for ele in jsonlist]))
        redis_df = pd.DataFrame(
            tasks_faissnv_v1.json_loads_error_fname(
                newjsonlist, deserialize=deserialize
            )
        )
        redis_df = redis_df[columns_to_read]

        return redis_df
    else:
        return pd.DataFrame(columns=columns_to_read)


def merge_prlm(res_df, prlm_df, prlm_mpe_name=""):
    """
    This function merges the results of prlm with both the ecips_db and redis database.

    Inputs:
        res_df - aggregate ecips_db and redis database
        prlm_df - loaded prlm dataframe
        prlm_mpe_name - name of mpe folder places (i.e. APBS-1, SPSS-2)
    Outputs:
        res_df - merged res_df and prlm_df
    """
    # filter by mpe type
    logging.debug(f"Merging results of {str(prlm_df)} with {str(res_df)} and ecips_db")
    if prlm_mpe_name != "":
        res_df = res_df[res_df["mpe_device"] == prlm_mpe_name].copy()

    res_df["filename"] = res_df["img_filepath"].apply(lambda x: x.split("/")[-1])
    prlm_df["filename"] = prlm_df["image_path"].apply(lambda x: x.split("/")[-1])
    res_df = res_df.merge(
        prlm_df[["filename", "ocr_data", "bcr_data"]], on="filename", how="inner"
    )

    return res_df


def write_json(results, json_path):
    """
    This function writes the dangerous mail results to a json

    Inputs:
        results - all processing results
        json_path - path to write json
    """
    logging.debug(f"Writing dangerous mail results to {json_path}")
    with open(json_path, "w") as fp:
        try:
            json.dump(results, fp, indent=4)
        except Exception:
            json.dump(results.to_dict(orient="index"), fp, indent=4)


def compare_results(old_results, new_results):
    """
    Compares two results dataframes and returns the new results #,
    Matches on filepath

    Input:
        old_results
        new_results
    Output:
        new_results - results only in new_json
    """
    logging.debug(f"Comparing {str(old_results)} to {str(new_results)}, dropping duplicates")
    # compare jsons to see if they have unique images
    new_results = new_results[~new_results["filepath"].isin(old_results["filepath"])]
    new_results = new_results.drop_duplicates(subset=["filepath"])

    return new_results


def return_pvi_count(pvi_scores):
    """
    This function returns the number of PVI's detected

    Input:
        pvi_scores - scores from pvi model inference

    """
    logging.debug(f"Finding the length of {str(pvi_scores)}")
    if isinstance(pvi_scores, list):
        pvi_scores = np.array(pvi_scores)

    return len(pvi_scores[np.where(pvi_scores < SCORE_THRES)].flatten())


def process_barcode_value(x):
    logging.debug(f"Attempting to processing barcode value for {str(x)}")
    try:
        barcod_max_score = np.asarray(json.loads(x.barcode_scores)).flatten().max()
    except Exception:
        barcod_max_score = 0
    # If max barcode score > 0.8 or bcr_data is detected or barcode was valid
    # decoded than return true otherwise, return false
    if barcod_max_score > 0.8 or x.bcr_data != "" or x.barcode_valid == "True":
        return True
    else:
        return False


def process_results(res_df, risk_threshold=RISK_THRESHOLD):
    logging.debug(f"Processing results for {str(res_df)} with risk_threshold of {RISK_THRESHOLD}")
    res_df = res_df.rename(
        columns={
            "package": "package_type",
            "pvi": "pvi_present",
            "ocr_data": "zipcode",
            "num_stamps": "stamp_count",
            "img_filepath": "filepath",
        }
    )
    # New Calculations removed the need for this v1.3.0
    # try:
    #    res_df['stamp_count'] = res_df['stamp_count'].apply(lambda x:      #len(np.frombuffer(bytes.fromhex(x))))
    # except Exception:
    #    res_df['stamp_count'] = 0

    res_df[
        [
            "barcode_risk_score",
            "stamp_risk_score",
            "package_risk_score",
            "zipcode_risk_score",
            "pvi_risk_score",
        ]
    ] = 0
    res_df["composite_barcode_valid"] = res_df.apply(process_barcode_value, axis=1)
    res_df.loc[
        ~res_df["composite_barcode_valid"], "barcode_risk_score"
    ] = BARCODE_MODEL_WEIGHT
    res_df["pvi_count"] = res_df["pvi_scores"].apply(lambda x: return_pvi_count(x))

    logging.debug(f"Evaluating model risk scores for {str(res_df)}")
    res_df.loc[
        res_df.zipcode.isin(IMPORTANT_ZIP_LIST), "zipcode_risk_score"
    ] = ZIP_MODEL_WEIGHT
    res_df.loc[
        res_df.stamp_count > STAMP_THRESHOLD, "stamp_risk_score"
    ] = STAMP_MODEL_WEIGHT
    res_df.loc[res_df.pvi_count < PVI_THRESHOLD, "pvi_risk_score"] = PVI_MODEL_WEIGHT

    try:
        res_df.loc[
            res_df.package_type.isin(IMPORTANT_PACKAGE_CLASS), "package_risk_score"
        ] = PACKAGE_MODEL_WEIGHT
    except Exception:
        res_df.loc[
            res_df.package_type == IMPORTANT_PACKAGE_CLASS, "package_risk_score"
        ] = PACKAGE_MODEL_WEIGHT

    res_df["overall_risk_score"] = (
        res_df["barcode_risk_score"]
        + res_df["stamp_risk_score"]
        + res_df["package_risk_score"]
        + res_df["zipcode_risk_score"]
    )

    res_df = res_df[res_df["overall_risk_score"] > risk_threshold]

    return res_df


def calc_stats(results, res_df):
    """
    This function calculates the dangerous mail statistics for model inference results

    Inputs:
        results - looks unused
        res_df - dataframe of results
    Output:
        stats - calculated statistics
    """
    logging.debug(f"Calculating dangerous mail statistics for {str(res_df)} results")

    barcode_count = len(res_df[res_df["barcode_risk_score"] == BARCODE_MODEL_WEIGHT])
    stamp_count = len(res_df[res_df["stamp_risk_score"] == STAMP_MODEL_WEIGHT])
    package_count = len(res_df[res_df["package_risk_score"] == PACKAGE_MODEL_WEIGHT])
    zip_count = len(res_df[res_df["zipcode_risk_score"] == ZIP_MODEL_WEIGHT])
    pvi_count = len(res_df[res_df["pvi_risk_score"] == PVI_MODEL_WEIGHT])
    total_packages = len(res_df["filepath"])
    weighted_count = len(res_df[res_df["overall_risk_score"] > RISK_THRESHOLD])

    stats = {"pvi_count": pvi_count}
    stats["zip_count"] = zip_count
    stats["barcode_count"] = barcode_count
    stats["stamp_count"] = stamp_count
    stats["package_count"] = package_count
    stats["risky_packages"] = res_df.to_dict(orient="index")
    stats["total_mailpieces"] = total_packages
    stats["weighted_count"] = weighted_count

    return stats


def format_results_json(res_df, first):
    """
    This function formats the results, so they can be used for a WebAPAT API call

    Inputs:
        res_df - dataframe representation of processing results
        first - flag detailing if it is the first call
    Outputs:
        results - formatted results dictionary
        res_df - updated res_df
    """
    logging.debug(f"Formatting results for {str(res_df)} to be used in WebAPAT API call")
    results = {
        "secretkey": "testing-79a1-40a3-8f0b-6513658be4ac",
        "action": "dm_orig_list_from_ecip",
        "images": [],
    }
    # default for pvi_present
    res_df["pvi_present"] = "FALSE"
    res_df["ecip_ip"] = DEVICE_MAPPINGS["ip"]
    res_df["barcode_present"] = None
    if first:
        # convert device name to device ip
        res_df["mpe_device_ip"] = res_df["mpe_device"].apply(lambda x: MPE_MAPPINGS[x])
        res_df = res_df[
            [
                "filepath",
                "ecip_ip",
                "mpe_ip",
                "overall_risk_score",
                "zipcode_risk_score",
                "zipcode",
                "pvi_risk_score",
                "pvi_present",
                "barcode_risk_score",
                "barcode_present",
                "barcode",
                "stamp_risk_score",
                "stamp_count",
                "package_risk_score",
                "package_type",
                "bcr_data",
            ]
        ]
        res_df.columns = [
            "filepath",
            "ecip_ip",
            "mpe_device_ip",
            "overall_risk_score",
            "zipcode_risk_score",
            "zipcode",
            "pvi_risk_score",
            "pvi_present",
            "barcode_risk_score",
            "barcode_present",
            "barcode",
            "stamp_risk_score",
            "stamp_count",
            "package_risk_score",
            "package_type",
            "bcr_data",
        ]
    res_df = res_df.reset_index(drop=True)

    results["images"] = res_df[
        [
            "filepath",
            "ecip_ip",
            "mpe_device_ip",
            "overall_risk_score",
            "zipcode_risk_score",
            "zipcode",
            "pvi_risk_score",
            "pvi_present",
            "barcode_risk_score",
            "barcode_present",
            "barcode",
            "stamp_risk_score",
            "stamp_count",
            "package_risk_score",
            "package_type",
            "bcr_data",
        ]
    ].to_dict(orient="index")

    logging.info(f"Results being sent to WebAPAT for {str(res_df)}: {results}")

    return results, res_df


def sendEmailAlert(
    stats,
    updated_stats,
    results,
    prlm_path,
    json_path="/home/webapat/dm/{datestr}.json".format(
        datestr=datetime.now().strftime("%Y%m%d")
    ),
):

    import smtplib
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    logging.debug(f"Sending email alert with results stats for {str(stats)}")

    smtpServer = "mailrelay.usps.gov"
    toAddr = ECIPS_EMAIL_ALERT_LIST
    fromAddr = "ecip-alert-mailer@usps.gov"  # Enter receiver address

    message = MIMEMultipart("alternative")
    message["Subject"] = "Risky Package Alert From ECIP Dev"
    message["From"] = fromAddr
    message["To"] = (", ").join(toAddr.split(","))

    risky_mailpieces = pd.DataFrame.from_dict(
        updated_stats["risky_packages"], orient="index"
    )["filepath"].apply(lambda x: x.split("/")[-1])

    html = (
        """\
    <html>
      <body>
        <p>
           Site: """
        + str(SITE)
        + """<br>
           Site Type: """
        + str(SITE_TYPE)
        + """<br>
           One or more risky mailpieces were identified in the following PRLM run: """
        + prlm_path
        + """ <br>
           Risky Zip: """
        + str(stats["zip_count"])
        + """<br>
           Risky PVI: """
        + str(stats["pvi_count"])
        + """<br>
           Risky Barcode: """
        + str(stats["barcode_count"])
        + """<br>
           Risky Stamp: """
        + str(stats["stamp_count"])
        + """<br>
           Risky Package: """
        + str(stats["package_count"])
        + """<br>
           Mailpiece is sent straight to risk folder: """
        + str(stats["zip_count"])
        + """<br>
           Weighted risk is over threshold: """
        + str(stats["weighted_count"])
        + """<br>
           Total risky mailpieces: """
        + str(len(stats["risky_packages"]))
        + """<br>
           Total mailpieces: """
        + str(stats["total_mailpieces"])
        + """<br>
           New Risky mailpieces: """
        + str(risky_mailpieces.to_dict())
        + """<br>
        </p>
      </body>
    </html>
    """
    )
    logging.debug(html)
    part1 = MIMEText(html, "html")
    message.attach(part1)

    filename = json_path

    with tempfile.NamedTemporaryFile(mode="wb+") as fp:

        fp.write(orjson.dumps(results, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS))

        fp.flush()

        with open(fp.name, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part2 = MIMEBase("application", "octet-stream")
            part2.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part2)

        # Add header as key/value pair to attachment part
        part2.add_header(
            "Content-Disposition", f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part2)
    try:
        server = smtplib.SMTP(smtpServer, 25)
        server.ehlo()
        server.starttls()

        server.send_message(message)  # NOSONAR
        # - Recipient list coded to a config file restricted to update by the same access as rewuired to install the
        #    application. No sensitive data is included.

        server.quit()
    except Exception:
        logging.error("Error Connection to server was rejected")


def convertColToInt(col):
    col = pd.to_numeric(col, errors="coerce")
    col[np.isnan(col)] = 0
    col = col.astype(int)
    return col


def procArCol(col):
    # procArCol removes various characters and cast the column
    # to an integer.
    try:
        # Set the known AR codes
        AR_CODES = ["%", "!", "/", "<", "{", "$", "[", "]", "}"]

        # Remove known AR codes
        for ac in AR_CODES:
            col = col.str.replace(ac, "")

        # Remove trailing characters
        col = col.str.replace("R", "")
        col = col.str.replace(" ", "")

        # Convert column to integer
        col = convertColToInt(col)
    except Exception:
        col = 0

    return col


def gen_cksum(barcode, modulus=10):
    try:
        checksum = modulus - (3 * sum(barcode[::2]) + sum(barcode[1::2])) % modulus
    except Exception:
        checksum = -1
    return checksum


def validate_barcode(barcode):
    try:
        dig_list = [int(i) for i in barcode]
        return dig_list[-1] == gen_cksum(dig_list[:-1])
    except Exception:
        return False


def parseBarcode(col):
    try:
        bcr_string_parsed = col.str.slice(11, 33)
    except Exception:
        bcr_string_parsed = ""
    return bcr_string_parsed


def create_filename(df):
    date_string = pd.to_datetime(df["image_capture_time"])
    return "{datestr}_{imageid}_T.tif".format(
        datestr=date_string.strftime("%Y%m%d_%H"), imageid=df["id"]
    )


def load_prlm(fPath):
    """
    This function loads prlm data

    Input:
        fPath - path to prlm file
    Output:
        prlm - loaded prlm data
    """
    fieldnames = [
        "id",
        "machine_number",
        "operation_number",
        "sort_plan",
        "station_number",
        "aru",
        "ar",
        "image_capture_time",
        "fast_mode_flag",
        "processing_time",
        "bcr_data",
        "ocr_data",
        "vcs_data",
        "keyed_data",
        "image_type",
        "dimension",
        "weight",
        "side",
        "bin",
        "image_path",
    ]

    if "SPSS" in fPath:
        fieldnames.remove("fast_mode_flag")
        prlm = pd.read_csv(fPath, names=fieldnames)
        prlm["image_path"] = prlm.apply(create_filename, axis=1)
    else:
        prlm = pd.read_csv(fPath, skiprows=APBS_HEADER_SIZE, names=fieldnames)

    # Cast machine_number to uint8
    prlm.machine_number = pd.to_numeric(prlm.machine_number, downcast="unsigned")

    # Cast operation number to uint16
    prlm.operation_number = pd.to_numeric(prlm.operation_number, downcast="unsigned")

    # Clean up AR column
    prlm.ar = procArCol(prlm.ar)

    # Clean up processing time
    prlm.processing_time = convertColToInt(prlm.processing_time)

    # Clean up BCR data
    prlm.bcr_data = prlm.bcr_data.str.replace("B", "")
    prlm.bcr_data = parseBarcode(prlm.bcr_data)
    # TODO: Handle varios entrees

    # Clean ocr data
    prlm.ocr_data = prlm.ocr_data.str.replace("Z", "")
    prlm.ocr_data = prlm.ocr_data.str.replace("<", "")

    # Split OCR data into ocr zip and oel
    # newDf = prlm.ocr_data.str.split("=",n = 1, expand = True)
    # prlm.ocr_data = convertColToInt(newDf[0])
    # Add oel column
    # prlm.oel = newDf[1]

    # Clean up vcs data
    prlm.vcs_data = prlm.vcs_data.str.replace("X", "")
    prlm.vcs_data = prlm.vcs_data.str.replace("{", "")
    prlm.vcs_data = convertColToInt(prlm.vcs_data)

    # Clean up keyed_data
    prlm.keyed_data = prlm.keyed_data.str.replace("L !", "")
    prlm.keyed_data = prlm.keyed_data.str.replace("K 4", "")
    prlm.keyed_data = convertColToInt(prlm.keyed_data)

    # Clean up image type
    prlm.image_type = prlm.image_type.str.replace("M ", "")

    # Clean up and parse dimension
    prlm.dimension = prlm.dimension.str.replace("V ", "")
    dims = prlm.dimension.str.split(" ", n=2, expand=True)
    prlm["length"] = pd.to_numeric(dims[0], downcast="unsigned")
    prlm["width"] = pd.to_numeric(dims[1], downcast="unsigned")
    prlm["height"] = pd.to_numeric(dims[2], downcast="unsigned")
    prlm.pop("dimension")

    # Clean up weight
    prlm.weight = prlm.weight.str.replace("W ", "")
    prlm.weight = convertColToInt(prlm.weight)

    # Clean up side
    # Consider removing as all APBSs only have top side
    prlm.side = prlm.side.str.replace("S ", "")

    # Clean up bin
    prlm.bin = prlm.bin.str.replace("N ", "")
    prlm.bin = convertColToInt(prlm.bin)

    return prlm


def compare_new_risk_score(
    results,
    json_path="/home/webapat/dm/{datestr}.json".format(
        datestr=datetime.now().strftime("%Y%m%d")
    ),
):
    """
    Compares two existing json to new dataframe and returns the new results #,
    Matches on filepath

    Input:
        results
        json_path
    Output:
        new_results - results only in new_jsos
    """
    # Read old json_path
    logging.debug(f"Comparing {json_path} to results for {str(results)}, returning new results")
    try:
        old_results = pd.read_json(json_path)
        old_results = pd.json_normalize(old_results["images"])
    except Exception:
        logging.error(f"{json_path} is empty")
        old_results = pd.DataFrame(columns=["filepath"])

    total_results = pd.DataFrame.from_dict(results["images"], orient="index")
    new_results = compare_results(old_results, total_results)

    return new_results


def write_results_to_json(
    results,
    res_df,
    json_path="/home/webapat/dm/{datestr}.json".format(
        datestr=datetime.now().strftime("%Y%m%d")
    ),
):
    """
    Writes results to json in /home/webapat/dm/YYYYMMDD.json to be consumed by webapat

    Input:
        results
        res_df
        json_path
    Output:
        new_results - results only in new_jsons
    """
    logging.debug(f"Writing results for {str(res_df)} to {json_path}")
    # proactively create dangerous mail folder if it does not exist
    if not os.path.exists(os.path.dirname(json_path)):
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

    logging.debug("Checking if a json for today's date exists")

    if not os.path.exists(json_path):
        logging.debug("Creating json for run")
        print(res_df.columns)
        # Check if results dataframe is greater than 0 and create json
        if len(res_df["filepath"]) > 0:
            with open(json_path, "wb") as fp:

                fp.write(orjson.dumps(results, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS))

            logging.debug(f"Sending email with risky images for {str(res_df)}")
        else:
            logging.debug("No risky packages found out of %d packages" % len(res_df))

    else:
        logging.debug("Json exists -- check for new risky images")
        new_results = compare_new_risk_score(results, json_path=json_path)

        # overwrite results json with new data
        with open(json_path, "wb") as fp:
            fp.write(orjson.dumps(results, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS))

        results, res_df = format_results_json(new_results, False)

    return results, res_df


def send_email_update(total_stats, updated_stats, results, res_df, prlm_path):

    if len(res_df) > 0:
        logging.debug(f"Sending new email with risky images for {str(res_df)}")
        sendEmailAlert(total_stats, updated_stats, results, prlm_path)

    else:
        logging.info(f"No new risky images detected for {str(res_df)}")

    return 0


@app.task
def calculate_risk_multiple_prlms(
    start=datetime.now() - timedelta(days=1), end=datetime.now(), prlm_paths=None
):
    """
    This is the main processing function that is called on after ECIPs DB update Calculation.

    Input:
        start - datetime object for start of search (start=datetime.now()-timedelta(days=1))
        end   - datetime object for end of search (end=datetime.now())
        prlm_paths - list (optional) if not specified all prlms changed in the specified time window
    """
    # if no prlm_s are passed calculate prlms
    if prlm_paths is None:
        prlm_paths = ecips_path.get_prlm(start, end)
    logging.debug(f"Processing beginning for {str(prlm_paths)}")
    search_day = end

    logging.debug(f"Loaded data from ecips_db and redis for {str(prlm_paths)}")
    ecips_df = load_ecips_db_for_risk(
        search_day, columns_to_read=columns_to_read, load_redis_db=True
    )

    for prlm_path in prlm_paths:
        process_prlm(ecips_df, prlm_path)

    return 0


def read_ecips_db(search_day, columns_to_read=columns_to_read):
    """
    This function reads a day of data from the ecips_db database and returns the columns.

    Input:
        search_day - python datetime object for searching ecips_db
        columns_to_read - list see ecips_config for defaults, columns to return
    Output:
        ecip_df - data collected from search_day ecips_db
    """

    filter_1 = (
        (ds.field("year") == search_day.year)
        & (ds.field("month") == search_day.month)
        & (ds.field("day") == search_day.day)
    )

    try:
        logging.debug("Loading today's data from ecips_db database")
        # TODO Re Implement Schema
        ecip_df = (
            ds.dataset(ECIPS_DATABASE, format="parquet", partitioning="hive")
            .to_table(filter=filter_1, columns=columns_to_read)
            .to_pandas()
        )

    except Exception:
        # TODO implement better exeception formatting.
        logging.error("No data from today to load from ecips db. DataFrame could not be processed")
        raise Exception
        # ecip_df = pd.DataFrame(columns=columns_to_read)

    return ecip_df


def load_ecips_db_for_risk(
    search_day, columns_to_read=columns_to_read, load_redis_db=True
):
    """
    This function loads the ecip_db to calculate risk.

    Input:
        search_day - python datetime object for searching ecips_db
        columns_to_read - list see ecips_config for defaults, columns to return
    Output:
        search_df - data collected from search_day ecips_db
    """

    logging.debug("Loading data from ecips_db to calculate risk")
    ecips_df = load_ecips_db(
        search_day, days_reverse=1, columns_to_read=columns_to_read
    )
    if load_redis_db:
        logging.debug("Loading data from redis")
        redis_df = load_redis()
        logging.debug("Merging ecips_db data and redis data")
        ecips_df = ecips_df.append(redis_df)

    return ecips_df


def output_reconstruction(ecips_df, prlm_path):
    logging.debug("Outputting reconstructed barcode message")


def process_prlm(ecips_df, prlm_path):

    prlm_load = False
    logging.debug("Starting PRLM Load: {prlm_path}".format(prlm_path=prlm_path))

    try:
        prlm = load_prlm(prlm_path)
        logging.debug("PRLM load complete")
        prlm_load = True
    except Exception:
        msg = "Failed to load PRLM file - aborting"
        logging.error(msg)
        return msg

    if prlm_load:
        res_df = merge_prlm(ecips_df, prlm, prlm_mpe_name=prlm_path.split("/")[2])
        logging.debug("Merging ecips_df and prlm_df")

        # Check if there is anything to process
        if res_df.shape[0] > 0:

            logging.debug("Processing results dataframe")
            res_df = process_results(res_df)
            logging.debug("Results processed")

            logging.debug("Formatting results")
            results, res_df = format_results_json(res_df, True)
            logging.debug("Results formatted")

            logging.debug("Calculating overall risk statistics")
            stats = calc_stats(results, res_df)
            logging.debug("Finished calculating risk statistics")
            json_path = os.path.join(
                "/home/webapat/dm/", prlm_path.replace("/images/", "")
            ).replace(".PRLM", ".json")

            # If dangerous mail pieces detected
            if stats["total_mailpieces"] > 0:
                logging.info(f"Writing new results to {json_path}")
                # Check against already reported results and return only new results, update json
                # /home/webapat/json
                new_results, new_res_df = write_results_to_json(
                    results, res_df, json_path=json_path
                )

                logging.debug("Calculating Stats on new results")
                new_stats = calc_stats(new_results, new_res_df)

                logging.debug("Sending Email update")
                send_email_update(stats, new_stats, new_results, new_res_df, prlm_path)
            else:
                logging.info("No New Results to process")

        else:
            logging.info("No results to process")

    return 0


@app.task
def calculate_risk(path, sleeptime=300):
    """
    This is the main processing function that is called on a PRLM monitoring trigger.

    Input:
        path - path to prlm file
        sleeptime(optional) - default = 300 seconds time to wait for images to process
    """
    search_day = datetime.now()
    logging.debug(
        f"Waiting 5minutes to allow images to process that may be reflected in {path}"
    )
    time.sleep(sleeptime)
    logging.debug(f"Processing beginning for {path}. Loading data from ecips_db and redis")
    ecips_df = load_ecips_db_for_risk(
        search_day, columns_to_read=columns_to_read, load_redis_db=True
    )

    process_prlm(ecips_df, path)
    logging.debug(f"Processing for {path} is finished")

    return 0
