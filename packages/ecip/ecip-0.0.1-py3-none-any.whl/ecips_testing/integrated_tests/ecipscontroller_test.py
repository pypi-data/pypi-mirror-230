import requests
from ecips_utils import ecips_config
# import os


# Test process Image Endpoint
def test_process_image_endpoint():

    ecips_controller_endpoint = ecips_config.ECIPS_CONTROLLER_ADDRESS

#    payload = {"photo_name":  os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/raw_images/003668.png",
#               "mpe_type": "MPE_001"
#               }

    payload = {"file_path": "/ECIPs/ecips_testing/ecips_test_files/raw_images/003668.png",
               "mpe_name": "MPE_001", "ignore_result": "FALSE"
               }

    r = requests.post('{ecips_controller_endpoint}/ProcessImage'.format(
            ecips_controller_endpoint=ecips_controller_endpoint), json=payload)
    assert r.status_code == 200


# Test searchImage Endpoint
def test_search_image_endpoint():

    ecips_controller_endpoint = ecips_config.ECIPS_CONTROLLER_ADDRESS

#    payload = {"photo_name":  os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/raw_images/003668.png",
#               "mpe_type": "MPE_001"
#               }

    payload = {"file_path": "/ECIPs/ecips_testing/ecips_test_files/raw_images/003668.png",
               "mpe_name": "MPE_001", "ignore_result": "FALSE"
               }

    r = requests.post('{ecips_controller_endpoint}/SearchImage'.format(
            ecips_controller_endpoint=ecips_controller_endpoint), json=payload)
    
    assert r.status_code == 200
