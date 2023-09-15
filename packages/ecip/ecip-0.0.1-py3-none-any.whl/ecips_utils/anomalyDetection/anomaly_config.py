import os
import json
from collections import namedtuple

# Creating an Anomaly Named tuple that allows us to group the Anomaly flag and assoc ID
Anomaly = namedtuple('Anomaly', ['is_active', 'anomaly_id', 'anomaly_class'])

# ANOMALY INDICATOR FLAGS, these are of class Anomaly defined above

# The anomaly where a hazmat symbol is found but the STC is not a Hazmat STC
HAZMAT_SYMBOL_STC_ANOMALY = Anomaly(json.loads(
    os.getenv("DETECT_HAZMAT_SYMBOL_STC_MISMATCH", default='true').lower()), "01", "hazmat")
# The anomaly where a hazmat H letter indicator is found but the STC is not a Hazmat STC
HAZMAT_LETTER_INDICATOR_STC_ANOMALY = Anomaly(json.loads(
    os.getenv("DETECT_HAZMAT_LETTER_INDICATOR_STC_MISMATCH", default='true').lower()), "02", "hazmat")
# The case where a ground advantage indicator (G or H) was used with a non-ground advantage STC Code
GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY = Anomaly(json.loads(
    os.getenv("GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY", default='true').lower()), "03", "ground-advantage")
# The case where a ground advantage indicator was not used but the STC corresponds to a ground advantage STC Code
NON_GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY = Anomaly(json.loads(
    os.getenv("NON_GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY", default='true').lower()), "04", "ground-advantage")
# The anomaly where a mail class banner contains verbiage for ground advantage but the
# STC does not correspond to a ground advantage STC
GROUND_ADVANTAGE_BANNER_STC_ANOMALY = Anomaly(json.loads(
    os.getenv("GROUND_ADVANTAGE_BANNER_STC_ANOMALY", default='true').lower()), "05", "ground-advantage")
# The anomaly where the permit imprint indicia contains ground advantage language, but the STC code does not
# correspond to a ground advantage STC
GROUND_ADVANTAGE_PERMIT_IMPRINT_INDICIA_STC_ANOMALY = Anomaly(json.loads(
    os.getenv("GROUND_ADVANTAGE_PERMIT_IMPRINT_INDICIA_STC_ANOMALY", default='true').lower()), "06", "ground-advantage")

# Grouping all Anomalies for group access
ANOMALY_TYPES = [HAZMAT_SYMBOL_STC_ANOMALY,
                 HAZMAT_LETTER_INDICATOR_STC_ANOMALY,
                 GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY,
                 NON_GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY,
                 GROUND_ADVANTAGE_BANNER_STC_ANOMALY,
                 GROUND_ADVANTAGE_PERMIT_IMPRINT_INDICIA_STC_ANOMALY]

# HAZMAT Anomaly Related Confidence Thresholds
# The minimum confidence required to be positive we have detected a hazmat H indicator
MIN_CONF_HAZMAT_H_INDICATOR = float(json.loads(
    os.getenv("MIN_CONF_HAZMAT_H_INDICATOR", default='0.95')))
# The minimum confidence thresholds for hazmat symbols (higher than that is sent to WebAPAT
# bc we want to be very confident and FN are okay
HIGH_CONF_HAZMAT_YOLO_SCORE_THRES = json.loads(os.getenv("HIGH_CONF_HAZMAT_YOLO_SCORE_THRES",
                                                         default='''
                                                               {"0":"",
                                                                "1": "0.83",
                                                                "2": "0.9",
                                                                "3": "",
                                                                "4": "1.0",
                                                                "5": "0.83",
                                                                "6": "",
                                                                "7": "1.0",
                                                                "8": "0.85",
                                                                "9": "",
                                                                "10": "",
                                                                "11": "",
                                                                "12": "",
                                                                "13": "",
                                                                "14": "",
                                                                "15": "",
                                                                "16": "0.83",
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
                                                                "27": "1.0"
                                                                }
                                                               '''))
MAX_GA_DIST = 3  # Max Levenshtein distance to "ground advantage" on permit-imprint
MAX_PRIORITY_DIST = 5  # Max Levenshtein distance to "priority" on permit-imprint
MAX_FC_DIST = 6  # Max Levenshtein distance to "first class" on permit-imprint

# Ground advantage confidence thresholds
MIN_CONF_GA_BANNER_TEXT = float(json.loads(
    os.getenv("MIN_CONF_GA_BANNER_TEXT", default='0.95')))

MIN_CONF_PRIORITY_P_INDICATOR = float(json.loads(
    os.getenv("MIN_CONF_PRIORITY_P_INDICATOR", default='0.93')))

MIN_CONF_FIRST_CLASS_F_INDICATOR = float(json.loads(
    os.getenv("MIN_CONF_FIRST_CLASS_F_INDICATOR", default='0.90')))

MIN_CONF_GROUND_G_INDICATOR = float(json.loads(
    os.getenv("MIN_CONF_GROUND_G_INDICATOR", default='0.93')))
