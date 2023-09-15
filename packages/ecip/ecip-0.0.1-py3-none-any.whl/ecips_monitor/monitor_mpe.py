from ecips_utils import ecips_config, ecips_path, ecips_health
import time
from datetime import datetime, timedelta
from celery import Celery
import os
from pathlib import Path
import logging

app = Celery(
    "tasks", broker=ecips_config.CELERY_BROKER, backend=ecips_config.CELERY_BACKEND
)

if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s %(message)s", level=ecips_config.LOGGING_LEVEL
    )  # NO SONAR
    # - Logs going to local Docker container and require server access with
    # access to said Docker container files to access.
    logging.getLogger(__name__)

    logging.debug("Start MPE processing for MPE folders in {}".format(ecips_config.ECIPS_MPE_LANDING_ZONE_PATH))
    waitDelay = 120  # seconds
    # Set initial window to be look back 120 seconds in case of failure
    end = datetime.now() - timedelta(seconds=waitDelay + 60*60)

    while True:
        start = end
        end = datetime.now()
        logging.debug(
            f"Processing MPE time between {start} and {end} from the last two days worth of MPE folders"
        )
        imageList = ecips_path.get_mpe_images(start, end)
        logging.debug(f"Number of Images to process is {len(imageList)}")
        existing_json_list = []
        new_image_list = []
        for image in imageList:
            payload = {
                "file_path": image,
                "mpe_type": image,
            }  # TODO enable mpe specific processing based on folder
            # Check if json exists and only send if .json  or lock file does not exist.
            img_ext = os.path.splitext(image)[1]
            if not (os.path.exists(image.replace(img_ext, ".json"))):
                lock_filename = image.replace(img_ext, ".lock")
                if not (os.path.exists(lock_filename)):
                    logging.info(payload)
                    app.send_task(
                        "ecips_tasks.tasks.compute_feature_from_filepath",
                        kwargs={"img_filepath": image},
                        ignore_result=True,
                        rate_limit=ecips_config.ECIP_IMG_RATELIMIT,
                        time_limit=ecips_config.ECIP_IMG_TIMELIMIT,
                        soft_time_limit=ecips_config.ECIP_IMG_TIMELIMIT,
                        queue="livemail",
                        expires=24*60*60,
                    )
                    # After file sent, execute creation of lock file
                    Path(lock_filename).touch(exist_ok=True)

                    new_image_list.append(image)
                else:
                    existing_json_list.append(image)
            else:
                existing_json_list.append(image)

        logging.info(f"{len(new_image_list)} images were queued for processing."
                     f"{len(existing_json_list)} images were already processed and not sent."
                     )
        logging.debug("MPE processing complete for MPE folders in {} is complete."
                      .format(ecips_config.ECIPS_MPE_LANDING_ZONE_PATH))

        # Wait 2 minutes before processing again.
        time.sleep(waitDelay)
        ecips_health.health_check(name="monitor_mpe")
