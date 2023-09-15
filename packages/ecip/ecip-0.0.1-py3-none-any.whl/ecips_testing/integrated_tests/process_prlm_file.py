import glob
from ecips_utils import ecips_config
from celery import Celery
import time
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    app = Celery(
        "tasks_comms",
        broker=ecips_config.CELERY_BROKER,
        backend=ecips_config.CELERY_BACKEND,
    )

    parser.add_argument("-d", "--directory", help="Path to the directory containing prlm files you want to process")

    args = parser.parse_args()
    directory = args.directory

    prlms = glob.glob(directory + "/**/*.zip*", recursive=True)

    print(f"{len(prlms)} prlms total found to process in directory {directory} ")
    start_time = True
    for prlm in prlms:
        app.send_task(
            "ecips_tasks.tasks_comms.process_prlm_start",
            kwargs={"prlm_file": prlm},
            ignore_result=True,
            queue="communication-prlm",
            expires=24 * 60 * 60
        )
        # print timestamp for start time
        if start_time:
            start_time = False
            print(f"process_prlm_start : {time.time()}")

    print(f"Queued all prlms in {directory}.  See Flower @ localhost:9000 for details")
