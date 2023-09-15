import os
import json
import logging
import cv2
import faiss
import redis
import numpy as np
import pandas as pd
import pyarrow as pa
from celery import Celery
import pyarrow.parquet as pq
from datetime import datetime, timedelta
from ecips_tasks import tasks_beats, tasks_risks
from ecips_utils import ecips_config, ecips_path
from ecips_utils.packageObject.packageclass import compute_feature_fromcv2
import ujson
from tqdm import tqdm
from pyarrow import dataset as ds

# Create Celery App for Tasking
app = Celery(
    "tasks_faiss",
    broker=ecips_config.CELERY_BROKER,
    backend=ecips_config.CELERY_BACKEND,
)
app.conf.result_expires = 3 * 60 * 60
app.tasks.register(tasks_beats.faiss_health_check)
app.tasks.register(tasks_beats.dask_health_check)

# set log
logging.getLogger(__name__)

# Dimensionality of single feature
dimensions = ecips_config.ECIPS_REVERSE_IMAGE_FEAUREDIM
outroot = ecips_config.ECIPS_WEBAPAT_OUTPUT_PATH

# Dask metadata in case chunk sizes don't allow proper inference of metadata
meta = ecips_config.ECIPS_DASK_META_DATA

# System configs
DEVICE_MAPPINGS = ecips_config.ECIPS_DEVICE_MAPPING
HUMAN_READABLE_NAME_MAPPINGS = ecips_config.ECIPS_DEVICE_MAPPING
HUMAN_READABLE_SITE_NAME = ecips_config.ECIPS_SITE_NAME_MAPPING
HUMAN_READABLE_SITE_TYPE = ecips_config.ECIPS_SITE_TYPE_MAPPING
IP = DEVICE_MAPPINGS["ip"]
SITE = HUMAN_READABLE_SITE_NAME[IP]
SITE_TYPE = HUMAN_READABLE_SITE_TYPE[IP]

# Writing pyarrow schema
pa_meta = []
new_meta = {}
META = meta
for key in META.keys():
    if META[key] == "string":
        pa_meta.append((key, pa.string()))
        new_meta[key] = "string"

    elif META[key] == "int64":
        pa_meta.append((key, pa.int64()))
        new_meta[key] = "int64"

    else:
        pa_meta.append((key, pa.float64()))
        new_meta[key] = "float"
schema = pa.schema(pa_meta)

# Redis
R = redis.Redis(host=ecips_config.CELERY_BACKEND.split(":")[1].replace("//", ""))


def json_loads_error_fname(jsonfilelist, deserialize=True):
    logging.debug(f"Opening json files in {str(jsonfilelist)}")
    json_dict_list = []
    for jsonfilename in jsonfilelist:
        try:
            with open(jsonfilename) as fp:
                try:
                    search_record = ujson.load(fp)
                    if deserialize:
                        search_record["descriptorList"] = np.frombuffer(
                            bytes.fromhex(search_record["descriptorList"]), dtype=np.float32
                        )
                    json_dict_list.append(search_record)

                except Exception as e:
                    logging.error(f"{e} Invalid json : {jsonfilename}")
        except Exception as e:
            logging.error(f"{e} Missing json : {jsonfilename}")
    return json_dict_list


def load_index_from_redis(deserialize=False):
    logging.debug("Loading index for redis")
    search_json_list = list(set(R.lrange("dailyJson_filePath", 0, -1)))
    newjsonlist = list(set([ele.decode("utf-8") for ele in search_json_list]))
    json_df = pd.DataFrame(json_loads_error_fname(newjsonlist, deserialize=deserialize))
    if not json_df.empty:

        return json_df[["img_filepath", "descriptorList", "dateProcessed"]]
    else:

        return json_df


def load_index_from_parquet(
    ECIPS_DATABASE=ecips_config.REVERSE_IMAGE_DB_PATH,
    batch_size=25_000,
    search_day=datetime.now(),
):  # ecips_config.ECIPS_REVERSE_IMAGE_DAYSINMEMORY)):
    """
    This Function triggers a reload of the ECIPs Parquet Database
    Parameters:
    ECIPS_Database (str): Location of Parquet Database
    nFeatures (int):  The size of each Feature (Sift=128)
    Returns:
    list of pa.Table(): The Table for searching
    """

    logging.debug(f"Creating Index for {ECIPS_DATABASE}")

    # try:

    filter_1 = (
        (ds.field("year") == search_day.year)
        & (ds.field("month") == search_day.month)
        & (ds.field("day") == search_day.day)
    )
    ecip_batch_iterator = ds.dataset(
        ECIPS_DATABASE, format="parquet", partitioning="hive"
    ).to_batches(
        filter=filter_1,
        columns=["img_filepath", "descriptorList", "dateProcessed"],
        batch_size=25_000,
    )

    return ecip_batch_iterator


def binarize_image(imagePath, adaptive_threshold=True, morph_image=False):
    # Set erosion and dilation kernel size
    # kernel_size = 2

    # Create erosion and dilation kernel
    # kernel = np.ones((kernel_size, kernel_size), np.uint8)

    # Read in the image
    logging.debug(f"Reading and binarizing {imagePath}")
    img = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)

    # Global thresholding
    # ret,th1 = cv.threshold(img,127,255,cv.THRESH_BINARY)

    # Adaptive thresholding
    if adaptive_threshold:
        output_image = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 3
        )

    # Erode image
    # if constant.BINARIZE_ERODE:
    if morph_image:
        # ToDo implement morphology tests
        kernel = (5, 5)
        output_image = cv2.erode(output_image, kernel, iterations=1)
        output_image = cv2.dilate(output_image, kernel, iterations=1)

    return output_image


def process_df_for_search(batchdf, convert_hex_to_np=False):
    # In case we are directly converting to hex from a JSON.  We deserialize back to numpy farther up the chain
    logging.debug(f"Processing {str(batchdf)} for search")
    if convert_hex_to_np:
        batchdf["descriptorList"] = [
            np.frombuffer(bytes.fromhex(descriptoriterm), dtype=np.float32)
            for descriptoriterm in batchdf.descriptorList.values
        ]

    batchdf["descriptorList"] = [
        descriptoriterm.reshape(-1, 128)
        for descriptoriterm in batchdf.descriptorList.values
    ]
    batchdf["descriptorList"] = [
        descriptoriterm[~np.isclose(descriptoriterm.sum(axis=1), 11.313706)]
        for descriptoriterm in batchdf.descriptorList.values
    ]
    notNaId = [
        descriptoriterm.shape[0] != 0
        for descriptoriterm in batchdf.descriptorList.values
    ]

    logging.info(f"Count of NaIDs for {str(batchdf)} : {sum(notNaId)}")
    logging.info(f"Shape of {str(batchdf)} : {batchdf.shape}")
    batchdf = batchdf[notNaId]
    index_list = np.hstack(
        [
            np.linspace(idx, idx, num=descriptorArray.shape[0], dtype="int64")
            for idx, descriptorArray in enumerate(batchdf.descriptorList.values)
        ]
    )
    return batchdf, index_list


def calculate_matches_from_search(
    batchdf, unique_neighbors, distances, neighbors, max_returns=64, min_distance=20
):
    logging.debug(f"Calculating matches from search for {str(batchdf)}")
    match_distances = []
    match_neighbors = []
    match_row = []
    for un in unique_neighbors:
        match_distances_unit = []
        match_neighbors_unit = []
        for row_id, (neighbors_row, distance_row) in enumerate(
            zip(neighbors, distances)
        ):
            distance_feature = distance_row[neighbors_row == un]
            if len(distance_feature) > 1 and distance_feature[0] < min_distance:
                logging.debug(f"Length of Distance for {str(un)} : {len(distance_feature)}")
                logging.debug(f'dist0 = {distance_feature[0]}, dist1={distance_feature[1]}')
                if (
                    distance_feature[0] < 0.75 * distance_feature[1]
                ):  # Modified for perfect match Dist0
                    match_neighbors_unit.append(un)
                    match_distances_unit.append(distance_feature[0])
                    match_row.append(row_id)

            elif len(distance_feature) == 1 and distance_feature[0] < min_distance:
                match_neighbors_unit.append(un)
                match_distances_unit.append(distance_feature[0])
                match_row.append(row_id)

        if len(match_distances_unit) > 0:
            match_distances.append(match_distances_unit[0])
            match_neighbors.append(un)
    match_neighbors = np.array(match_neighbors)
    match_distances = np.array(match_distances) * 1000
    sdx = np.argsort(match_distances)
    match_neighbors = match_neighbors[sdx]
    match_distances = match_distances[sdx]
    maxmax = max_returns
    if len(match_neighbors) > maxmax:
        match_neighbors = match_neighbors[:maxmax]
        match_distances = match_distances[:maxmax]

    matches_df = batchdf.iloc[match_neighbors].copy()
    matches_df["distance"] = match_distances

    return matches_df


def search_dataframe(
    batchdf,
    index_list,
    descriptors,
    search_return=64 * 4,
    max_return=64,
    min_distance=10,
):
    logging.debug(f"Implementing search for {str(batchdf)}")
    res = faiss.StandardGpuResources()
    res.setDefaultNullStreamAllDevices()

    xb = np.vstack(batchdf["descriptorList"].values)
    logging.info(f"Search array for {str(batchdf)} is {xb.nbytes}")

    distances, neighbors_vector = faiss.knn_gpu(
        res, descriptors.astype(np.float32), xb, search_return
    )
    neighbors = index_list[neighbors_vector]

    # distances *= 1000.0
    # neighbors[distances < 10]
    unique_neighbors = np.unique(neighbors[distances < min_distance])
    logging.info(f"Unique neighbors for {str(batchdf)}  = {len(unique_neighbors)}")
    logging.info(f"Mean_distances for {str(batchdf)}  = {np.mean(distances[[distances < min_distance]])}")
    logging.debug(f"List of unique neighbors for {str(batchdf)} = {unique_neighbors}")
    matches_df = calculate_matches_from_search(
        batchdf,
        unique_neighbors,
        distances,
        neighbors,
        max_returns=max_return,
        min_distance=min_distance,
    )

    return matches_df


@app.task()
def search_for_matches_filepath(
    img_filepath,
    search_day=datetime.now(),
    search_today=True,
    maxReturns=ecips_config.REVERSE_IMAGE_SEARCH_RESULT_SIZE,
    writeToFile=False,
):
    """
    This Function triggers a Search of the FAISS Index
    If the FAISS index is not loaded, it will automatically load the index
    The  Function writes the results to file in a way nec
    Parameters:
    img_filepath (str): Location of Parquet Database
    Returns:
    json: Dictionary of results
    """

    # result_table_size = 0
    # for result_table in result_table_list:
    #    result_table_size = result_table_size + result_table.shape[0]

    # prepare directory for results
    logging.debug(f"Creating output folder for {img_filepath}")

    imgbasename = os.path.splitext(os.path.basename(img_filepath))[0]
    search_file_path = os.path.join(
        ecips_config.ECIPS_WEBAPAT_OUTPUT_PATH, imgbasename,
    )
    os.makedirs(search_file_path, exist_ok=True)

    # Computing Sift features for search
    logging.debug(f"Processing Image {imgbasename}".format(imgbasename=imgbasename))
    keypoints, descriptors = compute_feature_fromcv2(binarize_image(img_filepath))

    logging.debug(f"Performing search on {imgbasename}".format(imgbasename=imgbasename))

    logging.debug("Sift Feature INDEX For Processing")
    logging.debug(f"Loading INDEX for {search_day}".format(search_day=search_day.isoformat()))
    # Load Redis Database
    if search_today:
        logging.debug(f"Loading Redis INDEX for {search_day}".format(search_day=search_day.isoformat()))
        redis_table = load_index_from_redis()
    else:
        redis_table = pd.DataFrame()

    result_df_list = []

    if not redis_table.empty:
        logging.debug("Searching Redis Store for matches")
        batchdf, index_list = process_df_for_search(redis_table, convert_hex_to_np=True)
        matches_df = search_dataframe(
            batchdf,
            index_list,
            descriptors,
            search_return=64 * 4,
            max_return=64,
            min_distance=10,
        )
        if not matches_df.empty:
            result_df_list.append(matches_df)
        else:
            logging.info("No Matches Found in Redis Store")

    result_table_iterator = load_index_from_parquet(search_day=search_day)

    for result_table_batch in tqdm(result_table_iterator):
        batchdf = pa.Table.from_batches([result_table_batch]).to_pandas()

        if not batchdf.empty:
            # check if already converted to numpy array, if not convert
            # if not isinstance(batchdf.values[0], np.ndarray):
            batchdf, index_list = process_df_for_search(batchdf, convert_hex_to_np=True)
            matches_df = search_dataframe(
                batchdf,
                index_list,
                descriptors,
                search_return=64 * 4,
                max_return=64,
                min_distance=10,
            )
            if not matches_df.empty:
                result_df_list.append(matches_df)
            else:
                logging.info("No Matches Found")

    if len(result_df_list) > 0:
        result_df = pd.concat(result_df_list).sort_values("distance").head(n=maxReturns)
        # TODO sort by MPE
        mpe_dict = ecips_config.get_mpe_mappings()
        # logging.info(match_neighbors)
    else:
        result_df = pd.DataFrame()
        # write record to json_data for publishing of results

    json_data = []

    for idx, result_record in result_df.iterrows():
        json_data.append(
            {
                "filepath": result_record.img_filepath,
                "distance": int(result_record.distance),
                "mpe": ecips_path.calculate_ecips_path(result_record.img_filepath)[
                    "mpe_device"
                ],
            }
        )
    if len(json_data) > 0:
        df = pd.DataFrame(json_data)

        logging.debug(f"First few lines of json results: {df.head()}")
        logging.debug("Publishing json results")
        json_name = os.path.join(
            search_file_path, imgbasename + "_" + "total" + ".json"
        )
        logging.debug(f"Writing Files to {json_name}".format(json_name=json_name))

        if writeToFile:
            createWebApatJson(df, json_name)

            for (mpe_name, mpe_address) in mpe_dict.items():
                logging.debug(
                    f"Publishing results for {mpe_name} at {mpe_address}".format(
                        mpe_name=mpe_name, mpe_address=mpe_address
                    )
                )

                json_name = os.path.join(
                    search_file_path, imgbasename + "_" + mpe_address + ".json"
                )
                try:
                    createWebApatJson(df[df["mpe"] == mpe_name], json_name)
                except ValueError:
                    logging.info(
                        f" ValueError. Publishing 0 results for {mpe_name} at {mpe_address}".format(
                            mpe_name=mpe_name, mpe_address=mpe_address
                        )
                    )

        # Return DF
        return df.to_json(orient="records")
    else:
        return "{}"


def createWebApatJson(df, jsonName):
    resultsDict = {}
    for idx, record in df.reset_index().iterrows():
        recordDict = record.to_dict()
        recordDict.update({"relevant": 0})
        recordDict.pop("index", None)
        recordDict["filepath"] = recordDict["filepath"].replace(
            "/images/{mpe_device}/".format(mpe_device=recordDict["mpe"]), ""
        )
        recordDict.pop("mpe", None)
        resultsDict.update({idx: recordDict})

    with open(jsonName, "w") as fp:
        json.dump(resultsDict, fp, indent=4)


def json_loads_error(jsonString):
    try:
        parsed = json.loads(jsonString)
    except Exception as e:
        print(e)
        logging.debug(f"Invalid JSON for {str(jsonString)}")
        newjsonString = "{}"
        parsed = json.loads(newjsonString)
    return parsed


@app.task
def convert_results_toparquet(
    ecips_reverse_db_loc=ecips_config.REVERSE_IMAGE_DB_PATH,
    process_prlm=False,
    deserialize=False,
):

    """
    This Function converts json results from a set period of time to a parquet file dataset.
    Parameters:
    ecips_image_directory (str): Directory for all  images coming from MPE.
    start_date (str): ISOformat starting datetime for jsons to process
    end_day (str): ISOformat end datetime for jsons to process
    ecips_reverse_db_loc (str):  Directory for all Reverse
    Returns:
    int: 0
    """
    start_day = datetime.now().date().isoformat()
    logging.debug(f"Starting to process parquet for time: {start_day}")

    jsonlist = R.lrange("dailyJson_filePath", 0, -1)
    if jsonlist:
        newjsonlist = list(set([ele.decode("utf-8") for ele in jsonlist]))
        json_df = pd.DataFrame(
            json_loads_error_fname(newjsonlist, deserialize=deserialize)
        )

        # with ProgressBar():
        # df = mybag.to_dataframe(meta=meta).compute()
        pq.write_to_dataset(
            pa.Table.from_pandas(json_df, preserve_index=False),
            root_path=ecips_reverse_db_loc,
            partition_cols=["mpe_device", "year", "month", "day"],
        )

        R.ltrim("dailyJson_filePath", len(jsonlist), -1)

        end_day = datetime.now().date().isoformat()
        logging.debug(f"Finished process parquet for time range: {end_day}")

    else:
        logging.warning(
            f"No Jsons found from {start_day}".format(
                start_day=datetime.now().date().isoformat()
            )
        )
    if process_prlm:
        # ToDo Send To Task list
        tasks_risks.calculate_risk_multiple_prlms()

    return 0


@app.task(bind=True)
def search_for_matches_history(
    self, img_filepath, search_in_days=ecips_config.ECIPS_REVERSE_IMAGE_DAYSINMEMORY
):

    # self.update_state(state='PROGRESS', meta={
    # 'day': datetime.now().isoformat(), 'done': 1, 'total': int(searchInDays)})
    logging.debug(f"Searching for images within the last {search_in_days} days")
    dfjsonList = []
    dfjson = search_for_matches_filepath(
        img_filepath, search_day=datetime.now(), search_today=True, writeToFile=True
    )
    dfjsonList.append(dfjson)

    # self.update_state(state='PROGRESS', meta={
    # 'day': datetime.now().isoformat(), 'done': 1, 'total': int(searchInDays)})

    for day in range(search_in_days - 1):
        logging.debug(
            f"At day {day+1} of {search_in_days - 1} in search")
        dfjson = search_for_matches_filepath(
            img_filepath,
            search_day=datetime.now() - timedelta(days=day + 1),
            search_today=False,
            writeToFile=False,
        )
        dfjsonList.append(dfjson)
        # self.update_state(state='PROGRESS', meta={
        # 'day': datetime.now()-timedelta(days=day+1), 'done': day+1, 'total': searchInDays})

    dfConcat = []
    for dfjson in dfjsonList:
        df1 = pd.read_json(dfjson, orient="records")
        if df1.shape[0] > 0:
            dfConcat.append(df1)

    dfTotal = pd.concat(dfConcat)
    dfTotal = dfTotal.reset_index()
    dfTotal = dfTotal.sort_values(by="distance")

    writeToFile(
        img_filepath, dfTotal[0: ecips_config.REVERSE_IMAGE_SEARCH_RESULT_SIZE]
    )


def writeToFile(img_filepath, resultDF, mpe_dict=ecips_config.get_mpe_mappings()):

    logging.debug(f"Creating output folder for {img_filepath}")
    imgbasename = os.path.splitext(os.path.basename(img_filepath))[0]
    search_file_path = os.path.join(
        ecips_config.ECIPS_WEBAPAT_OUTPUT_PATH, imgbasename,
    )
    os.makedirs(search_file_path, exist_ok=True)

    jsonName = os.path.join(search_file_path, imgbasename + "_" + "total" + ".json")
    logging.debug(f"Writing Files to {jsonName}".format(jsonName=jsonName))

    if writeToFile:
        createWebApatJson(resultDF, jsonName)
        for (mpe_name, mpe_address) in mpe_dict.items():
            logging.debug(
                f"Publishing results for {mpe_name} at {mpe_address}".format(
                    mpe_name=mpe_name, mpe_address=mpe_address
                )
            )

            jsonName = os.path.join(
                search_file_path, imgbasename + "_" + mpe_address + ".json"
            )
            try:
                createWebApatJson(resultDF[resultDF["mpe"] == mpe_name], jsonName)
            except Exception:
                logging.debug(
                    f"Publishing 0 results for {mpe_name} at {mpe_address}".format(
                        mpe_name=mpe_name, mpe_address=mpe_address
                    )
                )
