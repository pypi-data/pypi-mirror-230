import os
import json
import pandas as pd
import logging

# Fraud Types:
FRAUD_TYPES = ["mismatch_humanReadableSN_decodedIBISN", "mismatch_humanReadableDate_decodedIBIDate",
               "invalid_eVS_permit", "missing_eVS_validation", "invalid_ePostage", "invalid_IBI_SN",
               "mismatch_mailclass_servicetype", "mismatch_mailclass_lettercode", "mismatch_hr_impb",
               "invalid_shippo_ePostage"]

# Fraud Indicators Flags
DETECT_MISSING_EPOSTAGE_COMPANYNAME = json.loads(
    os.getenv("DETECT_MISSING_EPOSTAGE_COMPANYNAME", default='true').lower())
DETECT_SHIPPO_EPOSTAGE_FRAUD = json.loads(
    os.getenv("DETECT_SHIPPO_EPOSTAGE_FRAUD", default='true').lower())
DETECT_INVALID_EVS_PERMIT = json.loads(
    os.getenv("DETECT_INVALID_EVS_PERMIT", default='true').lower())
DETECT_MISSING_EVS_VALIDATION = json.loads(
    os.getenv("DETECT_MISSING_EVS_VALIDATION", default='true').lower())

DETECT_IBI_DATE_MISMATCH = json.loads(
    os.getenv("DETECT_IBI_DATE_MISMATCH", default='true').lower())
DETECT_IBI_SN_MISMATCH = json.loads(
    os.getenv("DETECT_IBI_SN_MISMATCH", default='true').lower())

DETECT_SERVICETYPE_MISMATCH = json.loads(
    os.getenv("DETECT_SERVICETYPE_MISMATCH", default='true').lower())
DETECT_MAILCLASS_LETTERCODE_MISMATCH = json.loads(
    os.getenv("DETECT_MAILCLASS_LETTERCODE_MISMATCH", default='true').lower())

DETECT_IMPB_HR_MISMATCH = json.loads(
    os.getenv("DETECT_IMPB_HR_MISMATCH", default='true').lower())

DETECT_INVALID_IBI_SN = json.loads(
    os.getenv("DETECT_INVALID_IBI_SN", default='true').lower())

# IBI Fraud Config
DATE_RE = r'(^((\d{4}|\d{2}))\s*(-|/|1|\s)\s*((\d{2}))\s*(-|/|1|\s)\s*(\d{4}|\d{2}))|(^(\d{4}|\d{2})\s*(' \
          r'-|/|1|\s)\s*((\d{4}|\d{2}))\s*(-|/|1|\s)\s*((\d{2})))|(^([A-Z]{3}|[A-Z]{4})\s*\d{2}\s*\d{4})'
SERIAL_RE = r'^\d{3}(s|w|\d)(\d|o|c)+'

MIN_DATE_LEN = 8
MAX_DATE_LEN = 12

MIN_SERIAL_LEN = 10
MAX_SERIAL_LEN = 15

MAX_LEVENSHTEIN_DIST_IBI_DATE = 1
CONF_THRESHOLD_LEVEL_1 = 0.95
CONF_THRESHOLD_LEVEL_2 = 0.50
MAX_LEVENSHTEIN_DIST_IBI_DATE_LEVEL_1 = 1
MAX_LEVENSHTEIN_DIST_IBI_DATE_LEVEL_2 = 2
MAX_LEVENSHTEIN_DIST_IBI_DATE_LEVEL_3 = 3

MAX_LEVENSHTEIN_DIST_IBI_SN = 5
MAX_LEVENSHTEIN_DIST_IBI_SN_SPECIAL_DM = 4

DATE_FORMATS = ['%Y-%m-%d', '%Y-%b-%d', '%Y-%B-%d',  # 2022-08-27 2022-Aug-27 2022-August-27
                '%Y/%m/%d', '%Y/%b/%d', '%Y/%B/%d',  # 2022/08/27 2022/Aug/27 2022/August/27
                '%Y,%m,%d', '%Y,%b,%d', '%Y,%B,%d',  # 2022,08,27 2022,Aug,27 2022,August,27
                '%Y1%m1%d', '%Y1%b1%d', '%Y1%B1%d',  # 2022108127 20221Aug127 20221August127 (/ read as 1 by OCR)

                # '%y-%m-%d', '%y-%b-%d', '%y-%B-%d',  # 22-08-27 22-Aug-27 22-August-27
                # '%y/%m/%d', '%y/%b/%d', '%y/%B/%d',  # 22/08/27 22/Aug/27 22/August/27
                # '%y,%m,%d', '%y,%b,%d', '%y,%B,%d',  # 22,08,27 22,Aug,27 22,August,27
                # '%y1%m1%d', '%y1%b1%d', '%y1%B1%d',  # 22108127 221Aug127 221August127 (/ read as 1 by OCR)

                '%m-%d-%Y', '%b-%d-%Y', '%B-%d-%Y',  # 08-27-2022 Aug-27-2022 August-27-2022
                '%m/%d/%Y', '%b/%d/%Y', '%B/%d/%Y',  # 08/27/2022 Aug/27/2022 August/27/2022
                '%m,%d,%Y', '%b,%d,%Y', '%B,%d,%Y',  # 08,27,2022 Aug,27,2022 August,27,2022
                '%m1%d1%Y', '%b1%d1%Y', '%B1%d1%Y',  # 0812712022 Aug12712022 August12712022 (/ read as 1 by OCR)
                '%m/%d1%Y', '%m1%d/%Y',  # 08/2712022 08127/2022 (/ read as 1 by OCR)

                '%m%d%Y', '%b%d%Y', '%B%d%Y',  # 08272022 Aug272022 August272022 (- or / missed)
                '%m/%d%Y', '%m%d/%Y', '%m-%d%Y',  # 08/272022 0827/2022 08-272022 (- or / missed)
                '%m%d-%Y', '%m1%d%Y', '%m%d1%Y',  # 0827-2022 081272022 082712022 (- or / missed)

                '%m-%d-%y', '%b-%d-%y', '%B-%d-%y',  # 08-27-22 Aug-27-22 August-27-22
                '%m/%d/%y', '%b/%d/%y', '%B/%d/%y',  # 08/27/22 Aug/27/22 August/27/22
                '%m,%d,%y', '%b,%d,%y', '%B,%d,%y',  # 08,27,22 Aug,27,22 August,27,22
                '%m1%d1%y', '%b1%d1%y', '%B1%d1%y',  # 08127122 Aug127122 August127122 (/ read as 1 by OCR)
                '%m1%d/%y', '%m1%d/%y',  # 08127/22 08/27122

                '%m%d%y', '%b%d%y', '%B%d%y',  # 082722 Aug2722 August2722 (- or / missed)
                '%m/%d%y', '%m%d/%y', '%m-%d%y',  # 08/2722 0827/22 08-2722 (- or / missed)
                '%m%d-%y', '%m1%d%y', '%m%d1%y',  # 0827-22 0812722 0827022 (- or / missed)

                '%b%d,%Y', '%B%d,%Y', '%b%d,%y', '%B%d,%y',  # Aug27,2022 August27,2022 Aug27,22 August27,22
                ]

# Minimum confidence of the serial number
MIN_SERIAL_CONF = 0.4

# Permit Imprint Fraud Indicators Config
MAX_EPOS_DIST = 5
MAX_EVS_DIST = 2
MAX_PERMIT_DIST = 1
MIN_PERMIT_CONF = 0.1
MAX_PAID_DIST = 2
MAX_SHIPPO_DIST = 2
FUZZY_MATCH_PERMIT = os.getenv("FUZZY_MATCH_PERMIT", default=False)

INVALID_PERMIT_FILE = os.getenv("INVALID_PERMIT_FILE",
                                default="/ECIPs/Docker/Invalid_eVS_Permit_List.xlsx")

PERMIT_NO_COL = 'Invalid eVS Permit Number'
INVALID_PERMIT_NOS = None

SHIPPO_MIDS_FILE = os.getenv("SHIPPO_MIDS_FILE",
                             default="/ECIPs/Docker/SHIPPO_POPOUT_MIDS.xlsx")

MID_COL = 'MIDs'
VALID_SHIPPO_MIDS = None


def get_invalid_permits():
    """Do not call INVALID_PERMIT_NOS directly. It should only be accessed through this function
    Returns: _type_ : INVALID_PERMIT_NOS list
    """
    global INVALID_PERMIT_NOS
    global INVALID_PERMIT_FILE
    global PERMIT_NO_COL

    if not INVALID_PERMIT_NOS:
        try:
            INVALID_PERMIT_NOS = set(pd.read_excel(INVALID_PERMIT_FILE)[PERMIT_NO_COL].astype(str))
            logging.info(f"Successfully loaded Invalid permit numbers from file {INVALID_PERMIT_FILE}")
        # TODO: Mary - what exception might occur here? can we narrow it down?
        except Exception as e:
            logging.error(f"Unable to load invalid permit numbers for file {INVALID_PERMIT_FILE}. Error Code {e}")
            INVALID_PERMIT_NOS = set()

    return INVALID_PERMIT_NOS


def get_valid_shippo_mids():
    """Do not call INVALID_PERMIT_NOS directly. It should only be accessed through this function
        Returns: _type_ : INVALID_PERMIT_NOS list
        """
    global VALID_SHIPPO_MIDS
    global SHIPPO_MIDS_FILE
    global MID_COL
    if not VALID_SHIPPO_MIDS:
        try:
            VALID_SHIPPO_MIDS = set(pd.read_excel(SHIPPO_MIDS_FILE)[MID_COL].astype(str))
            logging.info(f"Successfully loaded Invalid permit numbers from file {SHIPPO_MIDS_FILE}")
        # TODO: Mary - what exception might occur here? can we narrow it down?
        except Exception as e:
            logging.error(f"Unable to load invalid permit numbers for file {SHIPPO_MIDS_FILE}. Error Code {e}")
            VALID_SHIPPO_MIDS = set()

    return VALID_SHIPPO_MIDS


# STC Mail Markings Fraud Config
MAX_DIST_FIRST_CLASS = 3
MAX_DIST_PRIORITY_MAIL = 4
MAX_DIST_EXPRESS_MAIL = 4
MAX_DIST_GA_MAIL = 2
MCB_OCR_THRESH = 0.3

STC_DB_FILEPATH = os.getenv("STC_DB_FILE",
                            default="/ECIPs/Docker/stc_db.json")

STC_DB = None


def get_stc_db():
    global STC_DB_FILEPATH
    global STC_DB
    global DETECT_SERVICETYPE_MISMATCH

    if STC_DB is None:
        try:
            with open(STC_DB_FILEPATH, "r", encoding="utf-8") as fp:
                STC_DB = json.load(fp)
                logging.info(f"Successfully loaded STC database from file {STC_DB_FILEPATH}")
        except Exception as e:
            logging.error(f"Unable to load STC code from db for file {STC_DB_FILEPATH}. Error Code {e}")
            STC_DB = {}
            DETECT_SERVICETYPE_MISMATCH = False

    return STC_DB


# IMPB Fraud Config
MAX_DIST_IMPB = 6  # We are only comparing valid OCR barcodes so this lev distance should be very low
