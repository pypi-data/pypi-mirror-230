import json
import logging
import os
import redis
import pathlib
from celery import Celery

PROCESSING_QUEUE_TIMEOUT = 3 * 60 * 60
OCR_TIMELIMIT = int(os.getenv('OCR_TIMELIMIT', default=300))  # 300 seconds
OCR_RATELIMIT = str(os.getenv('OCR_RATELIMIT', default='30/m'))

ECIP_IMG_TIMELIMIT = int(os.getenv('ECIP_IMG_TIMELIMIT', default=30))  # 300 seconds
ECIP_IMG_RATELIMIT = str(os.getenv('ECIP_IMG_RATELIMIT', default='100/m'))

ECIPS_BASE_DIR = pathlib.Path(os.getenv("ECIPS_BASE_DIR",
                                        default=str(pathlib.Path(__file__).parent.absolute().parent.parent)))

# Health check configs
ECIPS_APPLICATION_CHECKS = os.getenv('ECIPS_APPLICATION_CHECKS', default=['monitor_prlm', 'monitor_webapat',
                                                                          'monitor_mpe', 'ecips_risks',
                                                                          'ecips_livemail', 'ecips_faiss',
                                                                          'ecips_serving', 'ecips_dask',
                                                                          'ecips_beats'])
ECIPS_SYSTEM_CHECKS = os.getenv('ECIPS_SYSTEM_CHECKS', default=['ecips_db', 'images'])

# Elastic configs
ELASTIC_ENDPOINT = os.getenv('ELASTIC_ENDPOINT', default='http://mrflvapodr3.usps.gov')  # NOSONAR
# - Communication is only along the internal docker network and therefore is local to the server itself
ELASTIC_SUMMARY_TOGGLE = os.getenv('ELASTIC_SUMMARY_TOGGLE', default=True)
ELASTIC_PORT = os.getenv('ELASTIC_PORT', default=8080)

# Binarization options
BINARIZE_ERODE = os.getenv("ECIPS_BINARIZE_ERODE", default=False)
BINARIZE_DILATE = os.getenv("ECIPS_BINARIZE_DILATE", default=False)

# TaskQue information
CELERY_BROKER = os.getenv("ECIPS_CELERY_BROKER", default="redis://localhost")
CELERY_BACKEND = os.getenv("ECIPS_CELERY_BACKEND", default="redis://localhost")

# TaskQue information (INFORMED ADDRESS)
IA_CELERY_BROKER = os.getenv(
    "INFORMED_ADDRESS_CELERY_BROKER", default="redis://localhost"
)
IA_CELERY_BACKEND = os.getenv(
    "INFORMED_ADDRESS_CELERY_BACKEND", default="redis://localhost"
)

# Logging Configuration
LOGGING_PATH = os.getenv("LOGGING_PATH", default=str(ECIPS_BASE_DIR.joinpath('ecips_data/logging/')))
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", logging.INFO)

# Main Task
ECIPS_CORRUPT_IMAGE_COUNT = int(os.getenv("ECIPS_CORRUPT_IMAGE_COUNT", default=0))

# SIFT / PYSIFT Configuration Settings
ECIPS_REVERSE_IMAGE_FEAUREDIM = int(os.getenv("ECIPS_REVERSE_IMAGE_FEAUREDIM",
                                              default=128))
ECIPS_REVERSE_IMAGE_NFEATURES = int(os.getenv("ECIPS_REVERSE_IMAGE_NFEATURES",
                                              default=1028))

ECIPS_REVERSE_IMAGE_ALGORITHM = os.getenv("ECIPS_REVERSE_IMAGE_ALGORITHM", "sift").lower()
ECIPS_REVERSE_IMAGE_SIFT_OCTAVES = int(os.getenv("ECIPS_REVERSE_IMAGE_SIFT_OCTAVES",
                                                 default=3))
ECIPS_REVERSE_IMAGE_SIFT_CONTRASTTHRESH = float(os.getenv("ECIPS_REVERSE_IMAGE_SIFT_CONTRASTTHRESH",
                                                          default=0.04))

ECIPS_REVERSE_IMAGE_SIFT_EDGETHRESH = float(os.getenv("ECIPS_REVERSE_IMAGE_SIFT_EDGETHRESH",
                                                      default=10))
ECIPS_REVERSE_IMAGE_SIFT_SIGMA = float(os.getenv("ECIPS_REVERSE_IMAGE_SIFT_SIGMA",
                                                 default=1.6))

# Reverse Image Settings
REVERSE_IMAGE_SEARCH_RESULT_SIZE = int(os.getenv("REVERSE_IMAGE_SEARCH_RESULT_SIZE",
                                                 default=64))
ECIPS_REVERSE_IMAGE_DAYSINMEMORY = int(os.getenv("ECIPS_REVERSE_IMAGE_DAYSINMEMORY",
                                                 default=14))

ECIPS_REVERSE_IMAGE_SEARCH_FAISS_GPU = bool(os.getenv("ECIPS_REVERSE_IMAGE_SEARCH_FAISS_GPU", default=False))
REVERSE_IMAGE_DATA_PATH = os.getenv("REVERSE_IMAGE_DATA_PATH",
                                    default="/mnt/database/ecips_db/")

REVERSE_IMAGE_DB_PATH = os.getenv("REVERSE_IMAGE_DB_PATH",
                                  default="/mnt/database/ecips_db/")

# TODO Remove soon
REVERSE_IMAGE_SEARCH_FEATURE_SIZE = os.getenv("REVERSE_IMAGE_SEARCH_FEATURE_SIZE",
                                              default=128)
# Controller Database Location:
ECIPS_CONTROLLER_ADDRESS = os.getenv("ECIPS_CONTROLLER_ADDRESS",
                                     default="http://docker_ecips_controller_1:8000")  # NOSONAR
# - Communication is only along the internal docker network and therefore is local to the server itself
# TODO AutoCreate Data Structure if it doesn't exist

# Risk calculation
ECIPS_BARCODE_MODEL_WEIGHT = os.getenv("ECIPS_BARCODE_MODEL_WEIGHT", default=0.25)
ECIPS_STAMP_MODEL_WEIGHT = os.getenv("ECIPS_STAMP_MODEL_WEIGHT", default=0.25)
ECIPS_PACKAGE_MODEL_WEIGHT = os.getenv("ECIPS_PACKAGE_MODEL_WEIGHT", default=0.25)
ECIPS_ZIP_MODEL_WEIGHT = os.getenv("ECIPS_ZIP_MODEL_WEIGHT", default=0.5)
ECIPS_PVI_MODEL_WEIGHT = os.getenv("ECIPS_PVI_MODEL_WEIGHT", default=0.1)
ECIPS_RISKS_THRES = os.getenv("ECIPS_RISKS_THRES", default=0.9)

# ECIPS_PACKAGE_MAPPINGS = os.getenv('ECIPS_PACKAGE_MAPPINGS', default={'no-package-label': 'other',
#                                                                       12: 'first-class',
#                                                                       16: 'priority mail'})
ECIPS_PACKAGE_MAPPINGS = os.getenv('ECIPS_PACKAGE_MAPPINGS', default={'no-package-label': 'other',
                                                                      5: 'first-class',
                                                                      6: 'priority',
                                                                      16: 'hazmat',
                                                                      17: 'express',
                                                                      18: 'first-class',
                                                                      21: 'ground-advantage'
                                                                      })
# ECIPS_PVI_MAPPINGS = os.getenv('ECIPS_PVI_MAPPINGS', default={18: 'pvi'})
ECIPS_PVI_MAPPINGS = os.getenv('ECIPS_PVI_MAPPINGS', default={4: 'pvi'})
# ECIPS_BARCODE_MAPPINGS = os.getenv('ECIPS_BARCODE_MAPPINGS', default={15: 'impb',
#                                                                       19: 's10'})
ECIPS_BARCODE_MAPPINGS = os.getenv('ECIPS_BARCODE_MAPPINGS', default={2: 'impb',
                                                                      1: 's10'})
ECIPS_HAZMAT_MAPPINGS = os.getenv('ECIPS_HAZMAT_MAPPINGS', default={0: 'Lithium_UN_Label',
                                                                    1: 'Lithium__Class_9',
                                                                    2: 'Lithium_Battery_Label',
                                                                    3: 'Biohazard',
                                                                    4: 'No_Fly',
                                                                    5: 'Finger_Small',
                                                                    6: 'Finger_Large',
                                                                    7: 'Cargo_Air_Only',
                                                                    8: 'Suspected_Label',
                                                                    9: 'Hazmat_Surface_Only',
                                                                    20: 'Cremated_Remains'})

ECIPS_YOLO_HAZMAT_MAPPINGS = os.getenv('ECIPS_YOLO_HAZMAT_MAPPINGS', default={0: None,
                                                                              1: 'Lithium_UN_Label',
                                                                              2: 'Lithium__Class_9',
                                                                              3: 'Lithium_Battery_Label',
                                                                              4: 'Biohazard',
                                                                              5: 'No_Fly',
                                                                              6: 'Finger_Small',
                                                                              7: 'Finger_Large',
                                                                              8: 'Cargo_Air_Only',
                                                                              9: 'Suspected_Label',
                                                                              10: '',
                                                                              11: None,
                                                                              12: None,
                                                                              13: None,
                                                                              14: None,
                                                                              15: None,
                                                                              16: 'Hazmat_Surface_Only',
                                                                              17: None,
                                                                              18: None,
                                                                              19: None,
                                                                              20: None,
                                                                              21: None,
                                                                              22: None,
                                                                              23: None,
                                                                              24: None,
                                                                              25: None,
                                                                              26: None,
                                                                              27: 'Cremated_Remains',
                                                                              28: 'Excepted_Quantity'})

ECIPS_IMPORTANT_ZIPS = os.getenv('ECIPS_IMPORTANT_ZIPS', default=['20500', '205000003', '20515', '20510'])
ECIPS_PRLM_HEADER_SIZE = os.getenv('ECIPS_PRLM_HEADER_SIZE', default=2)
ECIPS_STAMP_RISK_THRESHOLD = os.getenv('ECIPS_STAMP_RISK_THRESHOLD', default=20)
ECIPS_PVI_RISK_THRESHOLD = os.getenv('ECIPS_PVI_RISK_THRESHOLD', default=5)
ECIPS_EMAIL_ALERT_LIST = os.getenv('ECIPS_EMAIL_ALERT_LIST', default='''angela.m.su@usps.gov, stephen.e.tanner@usps.gov,
                                                                        Olufemi.T.AdedayoOjo@usps.gov,
                                                                        David.E.Lindenbaum@usps.gov''')
MAX_EMAIL_SIZE_MB = os.getenv('MAX_EMAIL_SIZE_MB', default=20)

# Dask
# TODO: update for pvi and package scores in format similar to hazmat
ECIPS_DASK_META_DATA = json.loads(os.getenv('ECIPS_DASK_META_DATA',
                                            default='''
                                            {"img_filepath": "string",
                                            "mpe_device": "string",
                                            "year": "int64",
                                            "month": "int64",
                                            "day": "int64",
                                            "plant_name": "string",
                                            "mpe_ip": "string",
                                            "key_pointsBytes": "string",
                                            "descriptorList": "string",
                                            "dateProcessed": "string",
                                            "barcode": "string",
                                            "detected_barcode": "string",
                                            "detected_digits": "string",
                                            "digit_scores": "string",
                                            "barcode_scores": "string",
                                            "barcode_valid": "string",
                                            "Barcode_model_version": "string",
                                            "Digit_model_version": "string",
                                            "pvi": "string",
                                            "pvi_scores": "string",
                                            "detected_pvi": "string",
                                            "PVI_model_version": "string",
                                            "num_stamps": "int64",
                                            "stamp_scores": "string",
                                            "detected_stamp": "string",
                                            "Stamp_model_version": "string",
                                            "package": "string",
                                            "Package_model_version": "string",
                                            "package_score": "float"
                                             }
                                            '''
                                            )
                                  )

# Triton Inference Server
ECIPS_INFERENCE_SERVER_USE_HAZMAT_YOLO = json.loads(
    os.getenv("ECIPS_INFERENCE_SERVER_USE_HAZMAT_YOLO", default='true').lower())
ECIPS_INFERENCE_SERVER_MAX_RETRIES = os.getenv("ECIPS_INFERENCE_MAX_RETRIES", default=3)
ECIPS_INFERENCE_SERVER_URL = os.getenv("ECIPS_INFERENCE_SERVER", default="ecips_serving:8000")
ECIPS_INFERENCE_SERVER_PROTOCOL = os.getenv("ECIPS_INFERENCE_SERVER_PROTOCOL", default="HTTP")
ECIPS_INFERENCE_BARCODE_MODEL_NAME = os.getenv("ECIPS_INFERENCE_BARCODE_MODEL_NAME", default="barcode")
ECIPS_INFERENCE_DIGIT_MODEL_NAME = os.getenv("ECIPS_INFERENCE_DIGIT_MODEL_NAME", default="digits")
ECIPS_INFERENCE_STAMP_MODEL_NAME = os.getenv("ECIPS_INFERENCE_STAMP_MODEL_NAME", default="stamp")
ECIPS_INFERENCE_PVI_MODEL_NAME = os.getenv("ECIPS_INFERENCE_PVI_MODEL_NAME", default="pvi")
ECIPS_INFERENCE_PACKAGE_MODEL_NAME = os.getenv("ECIPS_INFERENCE_PACKAGE_MODEL_NAME", default="package")
ECIPS_INFERENCE_BARCODE_VERSION = os.getenv("ECIPS_INFERENCE_BARCODE_VERSION", default=2)
ECIPS_INFERENCE_DIGIT_VERSION = os.getenv("ECIPS_INFERENCE_DIGIT_VERSION", default=3)
ECIPS_INFERENCE_STAMP_VERSION = os.getenv("ECIPS_INFERENCE_STAMP_VERSION", default=3)
ECIPS_INFERENCE_HAZMAT_VERSION = os.getenv("ECIPS_INFERENCE_HAZMAT_VERSION", default="1.0")
ECIPS_INFERENCE_PACKAGE_VERSION = os.getenv("ECIPS_INFERENCE_PACKAGE_VERSION", default="2.0")
ECIPS_INFERENCE_PVI_VERSION = os.getenv("ECIPS_INFERENCE_PVI_VERSION", default="2.0")
ECIPS_INFERENCE_YOLO_VERSION = os.getenv("ECIPS_INFERENCE_YOLO_VERSION", default="2.5")
ECIPS_INFERENCE_BATCH_SIZE = os.getenv("ECIPS_INFERENCE_BATCH_SIZE", default=1)
ECIPS_INFERENCE_VERBOSE = os.getenv("ECIPS_INFERENCE_VERBOSE", default=False)
ECIPS_INFERENCE_STREAMING = os.getenv("ECIPS_INFERENCE_STREAMING", default=False)
ECIPS_INFERENCE_IOU_THRES = os.getenv("ECIPS_INFERENCE_IOU_THRES", default=.8)
ECIPS_INFERENCE_SCORE_THRES = os.getenv("ECIPS_INFERENCE_SCORE_THRES", default=.3)
ECIPS_INFERENCE_STAMP_SCORE_THRES = float(os.getenv("ECIPS_INFERENCE_STAMP_SCORE_THRES", default=0))
ECIPS_INFERENCE_STAMP_IOU_THRES = os.getenv("ECIPS_INFERENCE_STAMP_IOU_THRES", default=.8)
ECIPS_INFERENCE_PACKAGE_SCORE_THRES = float(os.getenv("ECIPS_INFERENCE_PACKAGE_SCORE_THRES", default=.3))
ECIPS_INFERENCE_PACKAGE_IOU_THRES = os.getenv("ECIPS_INFERENCE_PACKAGE_IOU_THRES", default=.8)
ECIPS_INFERENCE_HAZMAT_SCORE_THRES = float(os.getenv("ECIPS_INFERENCE_HAZMAT_SCORE_THRES", default=0.67))
ECIPS_INFERENCE_HAZMAT_YOLO_SCORE_THRES = json.loads(os.getenv("ECIPS_INFERENCE_HAZMAT_YOLO_SCORE_THRES",
                                                               default='''
                                                               {"0":"",
                                                                "1": "0.73",
                                                                "2": "0.76",
                                                                "3": "",
                                                                "4": "0.9",
                                                                "5": "0.76",
                                                                "6": "0.8",
                                                                "7": "0.84",
                                                                "8": "0.75",
                                                                "9": "",
                                                                "10": "",
                                                                "11": "",
                                                                "12": "",
                                                                "13": "",
                                                                "14": "",
                                                                "15": "",
                                                                "16": "0.72",
                                                                "17": "",
                                                                "18": "",
                                                                "19": "",
                                                                "20": "",
                                                                "21": "",
                                                                "22": "",
                                                                "23": "",
                                                                "24": "",
                                                                "25": "",
                                                                "26": "",
                                                                "27": "0.96"
                                                                }
                                                               '''))

ECIPS_INFERENCE_BARCODE_SCORE_THRES = float(os.getenv("ECIPS_INFERENCE_BARCODE_SCORE_THRES", default=0.4))
ECIPS_INFERENCE_TIMEOUT = json.loads(os.getenv("ECIPS_INFERENCE_TIMEOUT", default='15.0'))

# WATCHDOG INOTIFY Settings
ECIPS_MPE_FILE_EXTENSION_PATTERN = os.getenv("ECIPS_MPE_FILE_EXTENSION_PATTERN", default=["*.tif", "*.png", "*.jpg"])
ECIPS_MPE_FILE_IGNORE_PATTERN = os.getenv("ECIPS_MPE_FILE_IGNORE", default="")
ECIPS_MPE_LANDING_ZONE_PATH = os.getenv("ECIPS_MPE_LANDING_ZONE_PATH",
                                        default="/images/")

ECIPS_WEBAPAT_FILE_EXTENSION_PATTERN = os.getenv("ECIPS_WEBAPAT_FILE_EXTENSION_PATTERN",
                                                 default=["*.tif", "*.png", "*.jpg"])

ECIPS_WEBAPAT_LANDING_ZONE_PATH = os.getenv("ECIPS_WEBAPAT_LANDING_ZONE_PATH",
                                            default='/home/webapat/input/')
ECIPS_WEBAPAT_OUTPUT_PATH = os.getenv("ECIPS_WEBAPAT_OUTPUT_PATH",
                                      default='/home/webapat/output/')
ECIPS_WEBAPAT_IDD_VERSION = json.loads(os.getenv("WEBAPAT_IDD_VERSION", default="10"))

POST_WEBAPAT_MSG_TYPE = json.loads(os.getenv("POST_WEBAPAT_MSG_TYPE", default="""
                                           {
                                           "hz_orig_list_from_ecip": "true",
                                           "rbc_orig_list_from_ecip": "true",
                                           "fr_orig_list_from_ecip": "true",
                                           "mail_anomaly_list_from_ecip": "true"
                                           }
                                           """
                                             )
                                   )
POST_WEBAPAT_MSG_TYPE = {msg_key: bool(POST_WEBAPAT_MSG_TYPE[msg_key]) for msg_key in POST_WEBAPAT_MSG_TYPE}


# Replacing the PRLM FILE EXTENSION PATTERN because .zip files are more up to date on all MPE
# ECIPS_PRLM_FILE_EXTENSION_PATTERN = os.getenv("ECIPS_PRLM_FILE_EXTENSION_PATTERN", default=["*.PRLM", "*.prlm"])
ECIPS_PRLM_FILE_EXTENSION_PATTERN = os.getenv("ECIPS_PRLM_FILE_EXTENSION_PATTERN", default=["*.zip"])
ECIPS_PRLM_IGNORE_KWORDS = os.getenv("ECIPS_PRLM_IGNORE_KWORDS", default="NEW")

# ECIPS_DEVICE MAPPINGS
ECIPS_DEVICE_MAPPING = json.loads(os.getenv("ECIPS_DEVICE_MAPPINGS", default='{"name": "default", "ip": "10.0.0.1"}'))
# ECIPS_MPE MAPPINGS
# Removing ECIPS_MPE_MAPPING as a static var because it may change
# ECIPS_MPE_MAPPING = json.loads(os.getenv(
#     "ECIPS_MPE_INDEX",
#     default='''
#   {"mpe_device01": "10.0.0.1", "mpe_device02": "10.0.0.2",
#   "mpe_device03": "10.0.0.3", "mpe_device04": "10.0.0.4"}
#   '''))

# ECIPS_STIE MAPPINGS
# Implemented Try exception for how the environment variable was loaded due to a pythondotenv vs docker native load
# https://github.com/docker/compose/issues/7624
try:
    ECIPS_SITE_NAME_MAPPING = json.loads(os.getenv("ECIPS_SITE_NAME", default='{"10.0.0.1": "Testing"}'))
except Exception:
    ECIPS_SITE_NAME_MAPPING = json.loads(os.getenv("ECIPS_SITE_NAME", default='{"10.0.0.1": "Testing"}').strip("'\'"))

try:
    ECIPS_SITE_TYPE_MAPPING = json.loads(os.getenv("ECIPS_SITE_TYPE", default='{"10.0.0.1": "Testing"}'))
except Exception:
    ECIPS_SITE_TYPE_MAPPING = json.loads(os.getenv("ECIPS_SITE_TYPE", default='{"10.0.0.1": "Testing"}').strip("'\'"))

# ECIPS_DATABASE CLEANING
ECIPS_DB = os.getenv("ECIPS_DB", default='/mnt/database/ecips_db')
ECIPS_TMP = os.getenv("ECIPS_TMP", default='/mnt/database/ecips_db_temp')
ECIPS_BACKUP = os.getenv("ECIPS_BACKUP", default='/mnt/database/backup')
DAYS = os.getenv("DAYS", default=14)

# ECIPS WEBAPAT Communication
ECIPS_WEBAPAT_URL = os.getenv("WEBAPAT_URL", default="https://56.76.171.26/ecip-api/api/EcipRequest")
ECIPS_WEBAPAT_SECRET_KEY = os.getenv("WEBAPAT_SECRET_KEY", default="testing-79a1-40a3-8f0b-6513658be4ac")
ECIPS_WEBAPAT_MAX_JSON_IMGS = json.loads(
    os.getenv("ECIPS_WEBAPAT_MAX_JSON_IMGS", default="100"))
ECIPS_WEBAPAT_TIMEOUT = json.loads(
    os.getenv("ECIPS_WEBAPAT_TIMEOUT", default="90"))  # timeout message after 1.5 mins

# ECIPS IDD WebAPAT Fields:
ECIPS_IDD_BCR_KEYS = ['barcode_risk_score', 'barcode_present', 'barcode_reconstructed', 'barcode']

# ECIPS perform BCR on PRLM file flag
ECIPS_PERFORM_BCR = json.loads(
    os.getenv("ECIPS_PERFORM_BCR", default='true').lower())

# ECIPS detect fraud on PRLM file flag
ECIPS_DETECT_FRAUD = json.loads(
    os.getenv("ECIPS_DETECT_FRAUD", default='true').lower())

# ECIPS detect anomalies on PRLM file flag
ECIPS_DETECT_ANOMALY = json.loads(
    os.getenv("ECIPS_DETECT_ANOMALY", default='true').lower())
# ECIPS send anomalies on to WebAPAT
SEND_ANOMALY_MESSAGE = json.loads(
    os.getenv("SEND_ANOMALY_MESSAGE", default='false').lower())

# ECIPS Flags to write the results to a json file
WRITE_OCR_RESULTS = json.loads(
    os.getenv("WRITE_OCR_RESULTS", default='true').lower())
WRITE_BCR_RESULTS = json.loads(
    os.getenv("WRITE_BCR_RESULTS", default='true').lower())
WRITE_FRAUD_RESULTS = json.loads(
    os.getenv("WRITE_FRAUD_RESULTS", default='true').lower())
WRITE_ANOMALY_RESULTS = json.loads(
    os.getenv("WRITE_ANOMALY_RESULTS", default='true').lower())

ECIPS_IDD_BCR_HAZMAT_KEYS = ['barcode_risk_score', 'barcode_present', 'barcode', 'barcode_class']
MPE_LIST = ['APBS', 'APPS', 'SPSS', 'EPPS', 'PSM', 'HOPS']

ECIPS_HAZMAT_VALID_ID = os.getenv("ECIPS_HAZMAT_VALID_ID", default=None)
if ECIPS_HAZMAT_VALID_ID is not None:
    ECIPS_HAZMAT_VALID_ID = json.loads(ECIPS_HAZMAT_VALID_ID)
ECIPS_HAZMAT_INVALID_ID = json.loads(os.getenv("ECIPS_HAZMAT_INVALID_ID", default='[5.0, 6.0]'))
ECIPS_HAZMAT_INVALID_ID_DICT = json.loads(os.getenv("ECIPS_HAZMAT_INVALID_ID_DICT",
                                                    default='''{"5": "Finger_Small", "6": "Finger_Large"}'''))
ECIPS_HAZMAT_YOLO_INVALID_ID_DICT = json.loads(os.getenv("ECIPS_HAZMAT_YOLO_INVALID_ID_DICT",
                                               default='''{"6": "Finger_Small"}'''))

SEND_ADDRESS_BLOCK_TO_IA = os.getenv("SEND_ADDRESS_BLOCK_TO_IA", default=False)

MIN_IMG_WIDTH = int(300)  # pixels
MIN_IMG_HEIGHT = int(300)  # pixels

ECIPS_SHIPPING_LABEL_CLASSES = json.loads(os.getenv("SHIPPING_LABEL_MODEL_CLASSES",
                                                    default='''
                                                    {"0": "background",
                                                    "1": "s10",
                                                    "2": "impb",
                                                    "3": "address-block",
                                                    "4": "pvi",
                                                    "5": "first-class",
                                                    "6": "priority",
                                                    "7": "ibi",
                                                    "8": "imb",
                                                    "9": "address-block-handwritten",
                                                    "10": "permit-imprint",
                                                    "11": "Lithium_UN_Label",
                                                    "12": "No_Fly",
                                                    "13": "Finger_Large",
                                                    "14": "Finger_Small",
                                                    "15": "Cargo_Air_Only",
                                                    "16": "hazmat",
                                                    "17": "express",
                                                    "18": "fcm",
                                                    "19": "Cremated_Remains",
                                                    "20": "stamp",
                                                    "21": "ground-advantage"
                                                    }
                                                    '''
                                                    ))

# Convert the json string format to ints
ECIPS_SHIPPING_LABEL_CLASSES = {ECIPS_SHIPPING_LABEL_CLASSES[class_id]: int(class_id)
                                for class_id in ECIPS_SHIPPING_LABEL_CLASSES}

# JSON Results Keys
BARCODE_METRIC_KEYS = ["barcode", "detected_barcode", "barcode_scores", "detected_digits", "digit_scores",
                       "barcode_valid", "Barcode_model_version", "Digit_model_version"]
PACKAGE_METRIC_KEYS = ["package", "package_score", "Package_model_version"]
PVI_METRIC_KEYS = ["pvi", "pvi_scores", "detected_pvi", "PVI_model_version"]
STAMP_METRIC_KEYS = ["num_stamps", "stamp_scores", "detected_stamp", "Stamp_model_version"]
HAZMAT_METRIC_KEYS = ["num_hazmat_labels", "hazmat_scores", "hazmat_classes", "detected_hazmat", "Hazmat_model_version"]
YOLO_METRIC_KEYS = ["yolo", "yolo_scores", "yolo_boxes", "yolo_classes", "YOLO_model_version"]

# Flag to do reconstructions on multiple barcodes
ECIPS_RECONSTRUCT_SINGLE_IMPB_BARCODE = json.loads(
    os.getenv("ECIPS_RECONSTRUCT_SINGLE_IMPB_BARCODE", default='false').lower())


def get_ia_celery_connection():
    app = Celery("tasks", broker=IA_CELERY_BROKER, backend=IA_CELERY_BACKEND)
    app.conf.result_expires = PROCESSING_QUEUE_TIMEOUT
    return app


R = None
ECIPs_VERSIONS = None


def get_redis_connection():
    global R

    if R is None:
        R = redis.Redis(host=CELERY_BACKEND.split(':')[1].replace("//", ""))

    return R


def get_ECIPs_versions():
    """
    The get_ECIPS_versions will return the ECIP version if the versions are correctly set
    otherwise it returns None
    """
    global ECIPs_VERSIONS

    if ECIPs_VERSIONS is None:
        ECIPs_VERSIONS = set_ECIP_versions()

    return ECIPs_VERSIONS


def get_mpe_mappings():
    # check if MPE mapping exists,
    # if not, set it the first time & return value
    # if it does, return val
    red = get_redis_connection()
    try:
        # load the value from redis
        mpe_mapping = red.get("ECIPS_MPE_MAPPING")
        # Initialize the ECIP versions variable
        get_ECIPs_versions()

        if mpe_mapping is not None:
            # return if it exists
            return json.loads(mpe_mapping)
        else:
            # if it doesnt exist, initialize the value and return the mpe_mappings
            set_mpe_mapping()

            return json.loads(red.get("ECIPS_MPE_MAPPING"))

    except redis.exceptions.ConnectionError:
        return json.loads(os.getenv(
            "ECIPS_MPE_INDEX",
            default='''
                                    {"mpe_device01": "10.0.0.1", "mpe_device02": "10.0.0.2",
                                    "mpe_device03": "10.0.0.3", "mpe_device04": "10.0.0.4"}
                                    '''))


def set_mpe_mapping():
    # Set the mpe mapping value from the environment variable.
    # Only takes place once as an initialization step
    try:
        get_redis_connection().set("ECIPS_MPE_MAPPING", os.getenv(
            "ECIPS_MPE_INDEX",
            default='''
              {"mpe_device01": "10.0.0.1", "mpe_device02": "10.0.0.2",
              "mpe_device03": "10.0.0.3", "mpe_device04": "10.0.0.4"}
              '''))
    except redis.exceptions.ConnectionError:
        # During unit tests, the redis db is not running and results in a
        # Connection refused error
        pass


def set_ECIP_versions():
    # Set the ecip versions from the environment variable.
    # Only takes place once as an initialization step
    # gets set the first time we set the MPE values
    try:
        get_redis_connection().set("ECIPS_SHIPPING_LABEL_MODEL_VERSION",
                                   os.getenv("ECIPS_INFERENCE_PACKAGE_VERSION", default="No Version Set"))

        get_redis_connection().set("ECIPS_HAZMAT_MODEL_VERSION",
                                   os.getenv("ECIPS_INFERENCE_HAZMAT_VERSION", default="No Version Set"))

        get_redis_connection().set("ECIPS_APPLICATION_VERSION",
                                   os.getenv("ECIP_VERSION", default="No Version Set"))

        return get_redis_connection().get("ECIPS_APPLICATION_VERSION")

    except redis.exceptions.ConnectionError:
        # During unit tests, the redis db is not running and results in a
        # Connection refused error
        return None
