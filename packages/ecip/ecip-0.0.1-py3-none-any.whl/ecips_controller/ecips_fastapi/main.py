import redis
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from ecips_tasks import tasks
from ecips_tasks import tasks_risks
from ecips_utils import ecips_config
from ecips_tasks import tasks_faissnv_v1

# Globals
R = redis.Redis(host=ecips_config.CELERY_BACKEND.split(':')[1].replace("//", ""))
SYS_KEYS = ecips_config.ECIPS_SYSTEM_CHECKS
APP_KEYS = ecips_config.ECIPS_APPLICATION_CHECKS
DEVICE_MAPPINGS = ecips_config.ECIPS_DEVICE_MAPPING
HUMAN_READABLE_SITE_NAME = ecips_config.ECIPS_SITE_NAME_MAPPING
HUMAN_READABLE_SITE_TYPE = ecips_config.ECIPS_SITE_TYPE_MAPPING
IP = DEVICE_MAPPINGS['ip']
SITE = HUMAN_READABLE_SITE_NAME[IP]
SITE_TYPE = HUMAN_READABLE_SITE_TYPE[IP]


class PrlmRun(BaseModel):
    file_path: str


class PackageImage(BaseModel):
    file_path: str
    mpe_name: str = None
    ignore_result: bool = True


class SearchImage(BaseModel):
    file_path: str


app = FastAPI(title="ECIP API",
              description="This API is built to drive ingest and Reverse Image Search on ECIPs devices",
              version="0.1.0",
              openapi_url="/api/v1/openapi.json")


def get_redis_values(major_key, minor_keys):
    '''
    This function is a helper function to build status dicts
    Inputs:
        major_key - identifier for system or application status
        minor_keys - associated keys with major flag
    '''
    status = {'site': SITE, 'site_type': SITE_TYPE}
    redis_live = R.ping()
    if not redis_live:
        return status.update({'redis': 'dead'})
    else:
        for key in minor_keys:
            value = R.get(f'{major_key}:{key}')
            if value is None:
                status[key] = 'dead'
            else:
                status[key] = value
        return status


@app.get("/SummaryStats")
async def summary_stats():
    '''
    This function gets summary stats for the ECIPs application
    '''
    stats = {
        'site': SITE,
        'site_type': SITE_TYPE,
        'images-processed': R.get('images-processed')
    }
    return stats


@app.get("/SystemHealth")
async def sys_health_check():
    '''
    This function checks system status
    '''
    status = get_redis_values('system-health', SYS_KEYS)
    return status


@app.get("/ApplicationHealth")
async def app_health_check():
    '''
    This function checks application status
    '''
    status = get_redis_values('application-health', APP_KEYS)
    return status


@app.post("/ProcessImage/")
async def processImage(item: PackageImage):
    """
    This function triggers a processing of a loaded image for calculation of it's search index
    Parameters:
    item (PackageImage): an img created by OpenCV imread Function
    Returns:
    celery.id:
    """

    logging.info("Processing image {photo_name} from {mpe_type}".format(photo_name=item.file_path,
                                                                        mpe_type=item.mpe_name)
                 )

    result = tasks.compute_feature_from_filepath.apply_async(
        kwargs={"img_filepath": item.file_path},
        ignore_result=item.ignore_result,
        expires=24*60*60,
        queue="livemail"
    )
    if item.ignore_result:
        result.forget()
        return 0

    return result.id


@app.post("/SearchImage")
async def searchImage(item: SearchImage):
    """
    This function triggers a search of a proposed action.  It calls a celery function  The tasks.tasks_faissnv
    Parameters:
    item (SearchImage): a item
    Returns:
    celery.id:
    """
    logging.info("Processing image {photo_name} for search".format(photo_name=item.file_path)
                 )

    result = tasks_faissnv_v1.search_for_matches_history.apply_async(
        kwargs={"img_filepath": item.file_path}, queue="faiss", expires=24*60*60
    )

    return result.id


@app.post("/CalcRiskScore")
async def calcRisk(item: PrlmRun):
    """
    This function triggers a risk score calculation for images referenced in a PRLM run.
    It calls the tasks.tasks_risks celery function.
    Parameters:
    item (PrlmRun): a item
    Returns:
    celery.id:
    """
    logging.info("Prompting risk calculation with PRLM run {file}".format(file=item.file_path)
                 )

    result = tasks_risks.calculate_risk.apply_async(
        kwargs={"path": item.file_path}, queue='dangerous_mail', expires=24*60*60)

    return result.id


# @app.post("/search/RebuildIndex")
# def rebuildIndex():
#    """
#    This function triggers a reload of the FAISS Index.  It calls a celery function  The tasks.tasks_faissnv
#
#
#    Parameters:
#    item (PackageImage): an img created by OpenCV imread Function
#
#    Returns:
#    celery.id:

#    """
#
#    result = tasks_faissnv.loadIndexFromParquet.apply_async(queue="index", ignore_result=True)
#
#    return result.id


# @app.get("/search/IndexStatus")
# async def getStatus():
# Todo Implement status check on Index
#    status = 0

#    return status
