"""
from ecips_tasks.tasks import app
import requests
import os
import time
from datetime import datetime, timedelta
import shutil
# TODO implement rsync speed test


def functionality_test():
    '''
    This function is the main processer for ensuring intended integrated
    application functionality.

    Returns:
        success_code - 0
    '''

    print("Running reverse image search test")
    for test_num in range(1,3):
        run_reverse_image_search(test_num)
        if test_num == 2:
            print("Reverse image search test complete")

    print("\nRunning image processing test")
    run_process_image()
    print("Image processing test complete")


def check_queues(queue_check, gain_check=False):
    '''
    This function checks if celery is still processing tasks for the extract
    queue.

    Input:
        queue_check - check to check
        gain_check - flag of whether to check if queue has been added to
    Returns:
        success_code - 0 or 1. Where 0 = success and 1 = fail
        gain_code - True or False
    '''

    url = 'http://ecips_flower:8888/api/workers'
    r = requests.get(url)
    content = r.json()
    keys = list(content.keys())

    for key in keys:
        if queue_check in key:
            queue_name = key

    i = app.control.inspect()
    if i.scheduled()[queue_name] != []:
        # tasks are still being scheduled
        success_code = 1
    elif i.active()[queue_name] != []:
        # tasks are still actively processing
        success_code = 1
    elif i.reserved()[queue_name] != []:
        # tasks are still awaiting processing
        success_code = 1
    else:
        success_code = 0
    
    if not gain_check:
        return success_code
    else:
        if success_code == 1:
            gain_code = True
        else:
            gain_code = False
        return gain_code


def run_reverse_image_search(test_num):
    '''
    This function runs the reverse image search integrated test

    Input:
        test_num: test # for reverse image search test
    '''

    while True:
        print("Checking extract queue")
        success_code = check_queues('extract')
        if success_code == 0:
            print(f"Extract queue clear testing reverse image search for test case {test_num}")
            # Processing for this test images is to fast so perform test multiple times.
            for i in range(10):
                trigger_monitor_webapat(test_num)

            print("Checking faiss queue")
            gains = check_queues('faiss', gain_check=True)
            assert gains == True, 'faiss queue was not added to'

            print("Faiss queue successfully added to")
            while True:
                success_code = check_queues('faiss')
                if success_code == 0:
                    print(f"Faiss queue is now clear. Proceeding ...")
                    break

                else:
                    print("Sleeping 10 seconds to allow faiss queue to finish processing")
                    time.sleep(10)
            break
        else:
            print("Sleeping 10 seconds")
            time.sleep(10)


def trigger_monitor_webapat(test_num):
    '''
    This function copying and moving files triggers api calls to the /SearchImage endpoint and 
    the subsequent processing done by tasks_faissnv_v1.searchForMatchesHistory 
    (i.e Reverse Image Search).

    Input:
        test_num: test # for reverse image search test

    Returns:
        success_code - 0
    '''

    if test_num == 1:
        cmd_1 = 'cp /home/webapat/input/000065A.png /home/webapat/000065A_1.tmp'
        cmd_2 = 'cp /home/webapat/000065A_1.tmp /home/webapat/input/000065A_1.tmp'
        cmd_3 = 'mv /home/webapat/input/000065A_1.tmp /home/webapat/input/000065A_1.png'
        os.system(cmd_1)
        os.system(cmd_2)
        os.system(cmd_3)

    else:
        cmd_1 = 'cp /home/webapat/000065A_1.tmp /home/webapat/000065A_2.tmp'
        cmd_2 = 'mv /home/webapat/000065A_2.tmp /home/webapat/input/000065A_2.png'
        os.system(cmd_1)
        os.system(cmd_2)

    return 0


def run_process_image():
    '''
    This function tests the mpe monitor capability, process api endpoint within ecips controller
    and the image processing capability.
    '''

    make_mpe_test_dir()

    print("For a maximum of 6 minutes checking that extract queue was added to")
    start = time.time()
    end = time.time()

    while end - start <= 360:
        gains = check_queues('extract', gain_check=True)
        end = time.time()

        # break 6 minute loop if processing finishes early
        if gains:
            break

    assert gains == True, 'extract queue was not added to'

    while True:
        print("Checking extract queue")
        success_code = check_queues('extract')
        if success_code == 0:
            print("Extract queue finished processing. Cleaning up files")
            remove_added_mpe_files()
            break


def make_mpe_test_dir():
    '''
    This function makes a temp directory within the watched directory
    to facilitate a monitor mpe governed integrated test
    '''

    # make testing directory
    if os.path.exists('/images/mpe_landing_test'):
        pass
    else:
        os.mkdir('/images/mpe_landing_test')

    today = datetime.today().strftime('%Y-%m-%d')
    yesterday = (datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')

    # make last two days worth of directories
    dates = [today, yesterday]
    for i in range(2):
        path = '/images/mpe_landing_test/'
        path += dates[i]
        os.mkdir(path)

        trigger_monitor_mpe(path)


def trigger_monitor_mpe(path):
    '''
    This function by rsyncing triggers api calls to the /ProcessImage endpoint and 
    the subsequent processing done by tasks.compute_feature_from_filepath.
    
    Input:
        path - destination of rsync
    '''
    
    # tirgger monitor mpe
    command = "rsync --recursive /ECIPs/ecips_testing/ecips_test_files/raw_images/ " + path
    status = os.system(command)
    assert status == 0, "rsysnc failed"

    # wrap the above in a rsync speed test


def remove_added_mpe_files():
    '''
    This function removes the resulting files and folders from testing.
    '''
    
    # delete files and folder
    shutil.rmtree('/images/mpe_landing_test/')
"""
