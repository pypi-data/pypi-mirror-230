from ecips_tasks import tasks
import time
from pathlib import Path
import glob
import dask.bag as db
import redis
from dask.diagnostics import ProgressBar
from ecips_utils import ecips_config
import os
import json
from dateutil.parser import parse as date_parser
from datetime import datetime, timedelta

# initializations
all_directories = []
update_directories = []
filepaths = []
num_partitions = 140
ecips_reverse_db_loc = ecips_config.REVERSE_IMAGE_DB_PATH
today = datetime.today()
two_weeks_ago = today - timedelta(days=14)
mpe_listings = ecips_config.get_mpe_mappings()

# Get relevant mpe folders
for mpe in mpe_listings:
    if 'mpe_landing_test' == mpe:
        pass
    else:
        all_directories.extend(glob.glob("/images/{}/**/".format(mpe)))

# Grab last two weeks worth of data
for directory in all_directories:
    directory_date = date_parser(Path(directory).stem)
    if directory_date > two_weeks_ago:
        update_directories.append(directory)

# Record directories to conduct inference on again
for directory in update_directories:
    filepaths.extend(list(map(str, Path(directory).rglob('*.tif'))))


# new crop and preproc version
async def prime(filepath):
    res = tasks.compute_feature_from_filepath.delay(filepath)
    return res


async def test_speed(runs, filepaths):
    delay_obs = []
    for i in range(runs):
        delay_obs.append(await (prime(filepaths[i])))

    obj_count = len(delay_obs)
    count = 0
    while count != obj_count:
        count = 0
        for obj in delay_obs:
            if obj.status == "SUCCESS":
                count += 1
runs = len(filepaths)
start = time.time()
await test_speed(runs, filepaths)
end = time.time()
proc_time = end-start

print("DATABASE REBUILDING TIME wasS " + str(proc_time))

meta = ecips_config.ECIPS_DASK_META_DATA

r = redis.Redis(
        host=ecips_config.CELERY_BACKEND.split(':')[1].replace("//", ""))
jsonList = r.lrange("dailyJson_filePath", 0, -1)

r.ltrim("dailyJson_filePath", len(jsonList), -1)
newjsonList = [ele.decode('utf-8') for ele in jsonList]
mybag = db.read_text(newjsonList).map(json.loads).repartition(npartitions=num_partitions)
new_df = mybag.to_dataframe(meta=meta)

if not os.path.exists('/mnt/database/upgrade/ecips_db'):
    os.makedirs('/mnt/database/upgrade/ecips_db')

with ProgressBar():
    new_df.to_parquet('/mnt/database/upgrade/ecips_db',
                      write_index=False,
                      append=False,
                      compression={"name": "gzip", "values": "snappy"},
                      partition_on=['mpe_device', 'year', 'month', 'day'],
                      engine='fastparquet',
                      ignore_divisions=True)
