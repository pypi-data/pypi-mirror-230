import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
import requests
from celery import Celery
import logging

from ecips_utils import ecips_config, ecips_path

app = Celery(
    "tasks_comms",
    broker=ecips_config.CELERY_BROKER,
    backend=ecips_config.CELERY_BACKEND,
)


if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s %(message)s", level=ecips_config.LOGGING_LEVEL
    )  # NO SONAR
    # - Logs going to local Docker container and require server access with access to
    # said Docker container files to access.
    logging.getLogger(__name__)

    logging.debug("Start PRLM processing for MPE folders in {}".format(ecips_config.ECIPS_MPE_LANDING_ZONE_PATH))
    waitDelay = 120  # seconds
    # Set initial window to be look back 120 seconds in case of failure
    end = datetime.now() - timedelta(seconds=waitDelay + 2)

    while True:
        start = end
        end = datetime.now()
        logging.debug(
            f"Processing PRLM time between {start} and {end} from the last two days worth of MPE folders"
        )
        prlmList = ecips_path.get_prlm(start, end)
        logging.debug(f"Number of PRLM files to process is {len(prlmList)}")
        existing_prlm_list = []
        new_prlm_list = []
        for prlm in prlmList:
            payload = {
                "file_path": prlm
            }  # TODO enable mpe specific processing based on folder
            prlm_ext = os.path.splitext(prlm)[1]
            lock_filename = prlm.replace(prlm_ext, ".lock")

            # Check if the corresponding .lock file exists
            lock_file_present = os.path.exists(lock_filename)

            # Check if keywords are present in the PRLM that indicate we should ignore this PRLM
            # This may occur during PRLM testing with the keyword "NEW" for example
            ignore_prlm_file = True if ecips_config.ECIPS_PRLM_IGNORE_KWORDS in prlm else False

            # If the lock file is not written and we dont want to ignore this file, then process the prlm
            if not lock_file_present and not ignore_prlm_file:
                logging.debug(f"Processing Results from PRLM file {prlm}")
                app.send_task(
                    "ecips_tasks.tasks_comms.process_prlm_start",
                    kwargs={"prlm_file": prlm},
                    ignore_result=True,
                    queue="communication-prlm",
                    expires=24*60*60
                )

                logging.info(payload)
                requests.post(
                    "{ecips_controller_endpoint}/CalcRiskScore".format(
                        ecips_controller_endpoint=ecips_config.ECIPS_CONTROLLER_ADDRESS
                    ),
                    data=json.dumps(payload),
                )
                Path(lock_filename).touch(exist_ok=True)
                new_prlm_list.append(prlm)
            else:
                existing_prlm_list.append(prlm)

        logging.info(f"{len(new_prlm_list)} prlms were queued for processing"
                     f"{len(existing_prlm_list)} prlms were already processed and not sent"
                     )
        logging.debug("PRLM processing for MPE folders in {} is complete."
                      .format(ecips_config.ECIPS_MPE_LANDING_ZONE_PATH))

        # Wait 2 minutes before processing again.
        time.sleep(waitDelay)
