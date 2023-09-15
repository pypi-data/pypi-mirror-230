import logging
import redis
import json
from celery import Celery
from copy import copy
from celery.schedules import crontab
from ecips_utils import ecips_config, ecips_health
from ecips_tasks import update_db
from ecips_utils.mpeDetection import create_envfiles

# Globals
R = redis.Redis(host=ecips_config.CELERY_BACKEND.split(':')[1].replace("//", ""))
URL = ecips_config.ECIPS_INFERENCE_SERVER_URL
PROTOCOL = "HTTP"  # ProtocolType.from_str(ecips_config.ECIPS_INFERENCE_SERVER_PROTOCOL)
MPE_MAPPINGS = ecips_config.get_mpe_mappings()

# Load Celery App
app = Celery('tasks_beats', broker=ecips_config.CELERY_BROKER, backend=ecips_config.CELERY_BACKEND)
app.conf.result_expires = 3 * 60 * 60

# Set up Celery Application heart beat tasks
app.conf.beat_schedule = {
    # Executes every hour
    'add-every-hour-parquet': {
        'task': 'ecips_tasks.tasks_faissnv_v1.convert_results_toparquet',
        'schedule': crontab(minute=0, hour='*/1'),
        'options': {'queue': 'dask'}
    },
    'update_database': {
        'task': 'ecips_tasks.tasks_beats.update_database',
        'schedule': crontab(minute='0', hour='0'),
        'options': {'queue': 'health-dask'}
    },
    'update_mpe_mappings': {
        'task': 'ecips_tasks.tasks_beats.update_mpe_mappings',
        'schedule': crontab(minute='0', hour='0'),
        'options': {'queue': 'health-dask'}
    },
    'clear_metric_counters': {
        'task': 'ecips_tasks.tasks_beats.clear_metric_counters',
        'schedule': crontab(minute='0', hour='0'),
        'options': {'queue': 'health-dask'}
    }
}


@app.task
def beats_health_check():
    """
    This function performs the application health check for ecips beats
    """
    logging.debug('Updating ecips_beats health status')
    ecips_health.health_check(name='ecips_beats')


@app.task
def livemail_health_check():
    """
    This function performs the application health check for ecips livemail
    """
    logging.debug('Updating ecips_livemail health status')
    ecips_health.health_check(name='ecips_livemail')


@app.task
def dask_health_check():
    """
    This function updates health status
    """
    logging.debug('Updating ecips_dask health status')
    ecips_health.health_check(name='ecips_dask')


@app.task
def risks_health_check():
    """
    This function updates health status
    """
    logging.debug('Updating ecips_risks health status')
    ecips_health.health_check(name='ecips_risks')


@app.task
def faiss_health_check():
    """
    This function updates health status
    """
    logging.debug('Updating ecips_faiss health status')
    ecips_health.health_check(name='ecips_faiss')


@app.task
def refresh_summary():
    """
    This function refreshes the summary statistics
    """
    logging.debug('Refreshing summary stats for MPE mappings')
    for mpe in MPE_MAPPINGS.keys():
        R.delete(f"image-processing:{mpe}")


@app.task
def check_db_memory():
    """
    This function performs a db memory utilization check
    """
    logging.debug(f'Checking ecips_db memory utilization on {ecips_config.REVERSE_IMAGE_DB_PATH}')
    mem_util = ecips_health.mem_utilization(directory_path=ecips_config.REVERSE_IMAGE_DB_PATH)
    logging.info(f'Ecips_db mem utilization is {mem_util}')


@app.task
def check_images_memory():
    """
    This function performs a memory utilization check for the images mount
    """
    logging.debug(f'Checking /images memory utilization for {ecips_config.ECIPS_MPE_LANDING_ZONE_PATH}')
    mem_util = ecips_health.mem_utilization(directory_path=ecips_config.ECIPS_MPE_LANDING_ZONE_PATH)
    logging.info(f'Images directory mem utilization is {mem_util}')


@app.task
def update_database():
    """
    This function performs database update
    """
    logging.debug('Cleaning database')
    update_db.main(ecips_config.ECIPS_DB, ecips_config.DAYS)


@app.task
def update_mpe_mappings():
    """
    This function scans the mounted drives for all MPE devices present
    """
    logging.debug('Updating the MPE mappings file')
    create_envfiles.main()

    logging.debug('Updating the MPE mappings value in redis')
    # Read the value from the new mpe_mappings.env file (written to above)
    mpe_path = '/ECIPs/Docker/mpe_mappings.env'
    with open(mpe_path, "r") as mpe_file:
        for line in mpe_file.readlines():
            if "ECIPS_MPE_INDEX" in line:
                mpe_mappings = line.split("=")[-1]

    if mpe_mappings != "{}":
        # Make a copy of the original MPE_Mappings dict and update with new info
        new_map = copy(ecips_config.get_mpe_mappings())
        new_map.update(json.loads(mpe_mappings))

        # Convert the dictionary back to json string
        new_map_json = json.dumps(new_map)

        # Update the Redis DB with the new MPE value
        R.set("ECIPS_MPE_MAPPING", new_map_json)
        logging.debug(f'Updated the MPE mappings value in redis to {new_map_json}')

    else:
        # Do not update if there are no mappings for MPEs
        # this can happen in instances when the remotempe volumes are not mounted
        logging.info("The MPE Mappings were not updated because no machines were found on the /remotempe drive")


@app.task
def clear_metric_counters():
    """
       This function resets redis counters to zero
    """
    logging.debug('Resetting the redis counters to zero')

    R.mset({"corrupt_image_count,bcr_count": 0,
            "small_image_count": 0,
            "mail_processed_count": 0,
            "hazmat_detection_count": 0,
            "bcr_count": 0,
            "mismatch_humanReadableSN_decodedIBISN": 0,
            "mismatch_humanReadableDate_decodedIBIDate": 0,
            "invalid_eVS_permit": 0,
            "missing_eVS_validation": 0,
            "invalid_ePostage": 0,
            "invalid_IBI_SN": 0,
            "mismatch_mailclass_servicetype": 0,
            "mismatch_mailclass_lettercode": 0,
            "mismatch_hr_impb": 0
            })
    logging.debug("Reset the counters to zero")
