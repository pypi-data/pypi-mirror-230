import json
import os
from ecips_utils import ecips_config

LOKI_USER_ID = os.getenv("LOKI_USER_ID", default='ecip_edge')
# make env var that gets pulled in through submission
# This would get set as a deployment var that gets set each time
ECIPS_IP = ecips_config.ECIPS_DEVICE_MAPPING["ip"]
LOKI_USER_PW = os.getenv("LOKI_USER_PW")
ECIP_HOST = ecips_config.ECIPS_DEVICE_MAPPING["name"]
MAX_LEN_LOKI_MSG = int(os.getenv("MAX_LEN_LOKI_MSG", default=100))

# Authorization
AUTH = (LOKI_USER_ID, LOKI_USER_PW)

# push msg log into grafana-loki
URL = os.getenv("LOKI_URL", default='https://eagnmnpodr3.usps.gov:443/api/prom/push')
HEADERS = json.loads(os.getenv("LOKI_HEADERS", default="""
                                           {
                                           "Content-type": "application/json",
                                           "X-Scope-OrgID": "tenantA"
                                           }
                                           """
                               )
                     )

POST_LOKI_MSG_TYPE = json.loads(os.getenv("POST_LOKI_MSG_TYPE", default="""
                                           {
                                           "hz_orig_list_from_ecip": "true",
                                           "rbc_orig_list_from_ecip": "true",
                                           "fr_orig_list_from_ecip": "true",
                                           "mail_anomaly_list_from_ecip": "true",
                                           "prlm_performance_from_ecip": "true",
                                           "image_results_from_ecip": "true"
                                           }
                                           """
                                          )
                                )
# Converting the strings to bool
POST_LOKI_MSG_TYPE = {msg_key: bool(POST_LOKI_MSG_TYPE[msg_key]) for msg_key in POST_LOKI_MSG_TYPE}
