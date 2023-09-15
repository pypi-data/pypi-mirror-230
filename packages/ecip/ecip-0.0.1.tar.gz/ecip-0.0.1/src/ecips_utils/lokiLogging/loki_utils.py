import requests
import json
import datetime
import pytz
import logging

from ecips_utils.lokiLogging.loki_config import URL, HEADERS, AUTH, ECIP_HOST, MAX_LEN_LOKI_MSG, ECIPS_IP


def post_loki_message(data,
                      source_name,
                      job_name,
                      url=URL,
                      headers=HEADERS,
                      auth=AUTH,
                      verify="/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem"):

    # If there is no data to post, skip this step
    if not data:
        return

    answers = []
    # Compile all the entries into one
    for start_index in range(0, len(data), MAX_LEN_LOKI_MSG):
        data_chunk = data[start_index:start_index + MAX_LEN_LOKI_MSG]
        entry = []
        for image_info in data_chunk:
            image_info["site_ip"] = ECIPS_IP
            entry.append({
                'ts': datetime.datetime.now(pytz.timezone('UTC')).isoformat('T'),
                'line': json.dumps(image_info)
            })

        payload = {
            'streams': [
                {
                    'labels': '{source="' + source_name + '",job="' + job_name + '", host="' + ECIP_HOST + '"}',
                    'entries': entry
                }
            ]
        }
        logging.debug(f"The following message will be sent to Grafana Loki {payload}")

        payload = json.dumps(payload)
        try:
            answer = requests.post(url,
                                   data=payload,
                                   headers=headers,
                                   auth=auth,
                                   verify=verify,
                                   timeout=10)
        except requests.exceptions.ConnectionError:
            # We want to catch this error and warn in the logs however we do NOT want to raise an error as
            # that could prevent us from sending messages to webapat
            logging.warning(f"Post to LOKI was unsuccessful for source {source_name} and job {job_name} "
                            f"due to a connection error with the LOKI URL {url}")
            return None

        except Exception as e:
            logging.warning(f"Post to LOKI was unsuccessful for source {source_name} and job {job_name} "
                            f"due to an unknown error {e}")
            return None

        logging.debug(f"Result from LOKI message post: {answer}")

        if answer.status_code != 204:
            # 204 is a successful message.  If it was not successful, print a warning message
            logging.warning(f"The post to LOKI was unsuccessful \n"
                            f"Status Code was: {answer.status_code} \n"
                            f"Text was: {answer.text} \n"
                            f"Reason was: {answer.reason}")
        else:
            # Message successfully posted
            logging.info(f"The post to LOKI was successful with status code {answer.status_code}\n"
                         f"source name is {source_name} \n"
                         f"job was: {job_name} \n")
            logging.debug(f"The following data was sent to loki {data}")

        answers.append(answer)
    return answers
