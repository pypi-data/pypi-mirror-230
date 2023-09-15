import logging
import requests
from ecips_utils import ecips_config


def post_webapat_message(results,
                         action,
                         webapat_url=ecips_config.ECIPS_WEBAPAT_URL,
                         webapat_secret_key=ecips_config.ECIPS_WEBAPAT_SECRET_KEY,
                         verify="/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",
                         headers={"Content-type": "application/json", "Accept": "text/plain"},
                         timeout=ecips_config.ECIPS_WEBAPAT_TIMEOUT):

    for json_index in range(0, len(results), ecips_config.ECIPS_WEBAPAT_MAX_JSON_IMGS):
        results_json = {
            "secretkey": webapat_secret_key,
            "action": action,
            "images": results[json_index:json_index + ecips_config.ECIPS_WEBAPAT_MAX_JSON_IMGS]
        }

        logging.info(f"The following JSON with items "
                     f"{json_index}/{json_index + ecips_config.ECIPS_WEBAPAT_MAX_JSON_IMGS} "
                     f"will be sent to WebAPAT for {action}: {results_json}\n")

        request = requests.post(
            webapat_url,
            json=results_json,
            verify=verify,
            headers=headers,
            timeout=timeout
        )

        request = request.json()
        logging.info(f"Message from the {action} WebAPAT Post: {request}")
