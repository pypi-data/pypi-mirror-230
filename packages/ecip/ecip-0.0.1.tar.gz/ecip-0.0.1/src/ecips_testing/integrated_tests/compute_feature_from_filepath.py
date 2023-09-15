import glob
import time
from ecips_utils import ecips_config
from celery import Celery
import time
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    app = Celery(
        "tasks", broker=ecips_config.CELERY_BROKER, backend=ecips_config.CELERY_BACKEND
    )

    parser.add_argument("-d", "--directory", help="Path to the directory containing image files you want to process")
    parser.add_argument("-w", "--wait", default=False,
                        help="Flag (bool) to determine if you would like to pause sending "
                             "in samples every 2000 or sample-size requests")
    parser.add_argument("-s", "--sample_size", default=2000,
                        help="Number of samples (int) to process before pausing to wait for processing to complete")

    args = parser.parse_args()
    directory = args.directory
    wait = args.wait
    sample_size = args.sample_size

    all_images = glob.glob(directory+"/**/*.tif*", recursive=True)

    print(f"{len(all_images)} Images total found to process in directory {directory} ")
    start_time = True

    sample_count = 0
    for image in all_images:
        app.send_task(
            "ecips_tasks.tasks.compute_feature_from_filepath",
            kwargs={"img_filepath": image},
            ignore_result=True,
            queue="livemail",
            expires=5 * 24 * 60 * 60  # 5 days because we are testing and may send in a big batch
        )
        if start_time:
            start_time = False
            print(f"compute_feature_from_filepath : {time.time()}")

        sample_count += 1

        # Every sample_size samples, pause before sending in additional samples
        if wait and sample_count >= sample_size:
            sample_count = 0
            # Pause for about 1 min per 1000 samples
            time_rest = int((sample_size // 1000) * 60)  # seconds
            print(f"Wait set to {wait}, resting for {time_rest} seconds before sending more data to queue")
            time.sleep(time_rest)

        sample_count += 1

        # Every sample_size samples, pause before sending in additional samples
        if wait and sample_count >= sample_size:
            sample_count = 0
            # Pause for about 1 min per 1000 samples
            time_rest = int((sample_size // 1000) * 60)  # seconds
            print(f"Wait set to {wait}, resting for {time_rest} seconds before sending more data to queue")
            time.sleep(time_rest)

    print(f"Queued all images in {directory}.  See Flower @ localhost:9000 for details")
