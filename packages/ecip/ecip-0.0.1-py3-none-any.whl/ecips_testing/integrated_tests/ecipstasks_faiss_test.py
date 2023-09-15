import pickle
from ecips_tasks.tasks_faissnv_v1 import (
  loadIndexFromParquet,
  loadIndexFromRedis,
  search_for_matches_filepath,
  convert_results_toparquet,
  addVectorToDatabase
)
import faiss
import glob
import json

def test_loadIndexFromParquet():
    path = '/ECIPs/ecips_testing/ecips_test_files/results/loadIndexFromParquet.dat'
    path_faiss = '/ECIPs/ecips_testing/ecips_test_files/results/loadIndexFromParquetFaiss.dat'
    with open(path, 'rb') as fp:
        gt_index_dict, gt_idx = pickle.dump(fp)
    gt_index = faiss.read_index(path_faiss)
    index, index_dict, idx = loadIndexFromParquet()
    assert index == gt_index, "faiss index is different then expected"
    assert index_dict == gt_index_dict, "dict is different than expected"
    assert gt_idx == idx, "idx is different then expected"


def test_loadIndexFromRedis():
    path = '/ECIPs/ecips_testing/ecips_test_files/results/loadIndexFromRedis.dat'
    path_faiss = '/ECIPs/ecips_testing/ecips_test_files/results/loadIndexFromRedisFaiss.dat'
    with open(path, 'rb') as fp:
        gt_index_dict, gt_idx = pickle.load(fp)
    gt_index = faiss.read_index(path_faiss)

    faiss_index, index_dict, idx = loadIndexFromParquet()
    index, index_dict, idx = loadIndexFromRedis(faiss_index, index_dict, idx)

    assert index == gt_index, "faiss index is different then expected"
    assert index_dict == gt_index_dict, "dict is different than expected"
    assert faiss_index.ntotal < index.ntotal, "function failed to add vectors"
    assert gt_idx == idx, "idx is different then expected"


def test_SearchForMatchesFilePath():
    filepaths = glob.glob("/images/APBS-1/2020-06-02/01-004/01-000/03/*.tif")
    sim_res = search_for_matches_filepath(filepaths[0])
    path = '/ECIPs/ecips_testing/ecips_test_files/results/SearchForMatchesFilePath.dat'
    with open(path, 'rb') as fp:
        gt_sim_res = pickle.load(fp)
    gt_sim_res = json.loads(gt_sim_res)[0]

    assert gt_sim_res['filepath'] == filepaths[0]


def test_convert_results_toparquet():
    status = convert_results_toparquet()
    assert status == 0, "error occured in conversion"


def test_addVectorToDatabase():
    path = '/ECIPs/ecips_testing/ecips_test_files/results/addVectorToDatabase.dat'
    with open(path, 'rb') as fp:
        search_json_list = pickle.load(fp)

    faiss_index, index_dict, idx = loadIndexFromParquet()
    count = faiss_index.ntotal
    for json_filepath in search_json_list:
        faiss_index, index_dict, idx = addVectorToDatabase(json_filepath, faiss_index, index_dict, idx, checkSize=False)
    new_count = faiss_index.ntotal
    assert new_count > count, "vectors were not added to index"
