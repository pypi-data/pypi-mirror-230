import os
from ecips_utils import ecips_config
from pyarrow import parquet as pq
import pyarrow as pa
import logging

# Load MetaData From Config
meta = ecips_config.ECIPS_DASK_META_DATA


# Writing pyarrow schema
pa_meta = []
new_meta = {}
META = meta
for key in META.keys():
    if META[key] == 'string':
        pa_meta.append((key, pa.string()))
        new_meta[key] = 'string'

    elif META[key] == 'int64':
        pa_meta.append((key, pa.int64()))
        new_meta[key] = 'int64'

    else:
        pa_meta.append((key, pa.float64()))
        new_meta[key] = 'float'

schema = pa.schema(pa_meta)

logging.debug("Grabbing database location from configs")
ecips_reverse_db_loc = ecips_config.REVERSE_IMAGE_DB_PATH

# Remove _common_metadata
item = os.path.join(ecips_reverse_db_loc, "_common_metadata")
if os.path.exists(item):
    logging.debug(f"_common_metadata found, Removing File {str(item)}")
    os.remove(item)
    logging.debug(f"{str(item)} removed")

else:
    logging.debug(f"_common_metadata not found, no need to remove file {str(item)}")

# remove _metadata
item = os.path.join(ecips_reverse_db_loc, "_metadata")
if os.path.exists(item):
    logging.debug(f"_metadata found, Removing File {str(item)}")
    os.remove(item)
    logging.debug(f"_metadata found, {str(item)} Removed")

else:
    logging.debug(f"_metadata not found, no need to remove file {str(item)}")

# Create new _metadata
logging.debug("Writing new _metadata")
pq.write_metadata(schema, "/mnt/database/ecips_db/_metadata")
