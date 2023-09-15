import json
from datetime import datetime, timedelta

import redis
from celery import Celery

from ecips_utils import ecips_config

# docker cp remove_old_tasks.py ecips_worker_gpu_faiss_v1:/app/
# docker exec -it ecips_worker_gpu_faiss_v1 python /app/remove_old_tasks.py


# Load Celery App
app = Celery(
    "tasks_comms",
    broker=ecips_config.CELERY_BROKER,
    backend=ecips_config.CELERY_BACKEND,
)

i = app.control.inspect()

# remove from Redis old livemail tasks
R = redis.Redis(host=ecips_config.CELERY_BACKEND.split(":")[1].replace("//", ""))
# search_json_list = list(R.lrange("livemail", 0, -1)))
newjsonlist = [json.loads(ele.decode("utf-8")) for ele in R.lrange("livemail", 0, -1)]
for json_dict in newjsonlist:
    task_name = json_dict['headers']['task']
    task_id = json_dict['headers']['id']
    try:
        task_kwargs = json.loads(json_dict['headers']['kwargsrepr'].replace("'", '"'))
        if 'compute_feature_from_filepath' in task_name.lower():
            img_filepath = task_kwargs['img_filepath']
            try:
                file_date = datetime.strptime(img_filepath.split("/")[3], "%Y-%m-%d")
                if file_date < (datetime.now() - timedelta(days=1)):
                    R.lrem('livemail', -2, json.dumps(json_dict))
            except Exception:
                try:
                    file_date = datetime.strptime(img_filepath.split("/")[3], "%Y%m%d")
                    if file_date < (datetime.now() - timedelta(days=1)):
                        R.lrem('livemail', -2, json.dumps(json_dict))
                except Exception:
                    print("error:")

        if 'ocr' in task_name.lower():
            img_filepath = task_kwargs['filepath']
            try:
                file_date = datetime.strptime(img_filepath.split("/")[3], "%Y-%m-%d")
                if file_date < (datetime.now() - timedelta(days=1)):
                    R.lrem('livemail', -2, json.dumps(json_dict))
            except Exception:
                try:
                    file_date = datetime.strptime(img_filepath.split("/")[3], "%Y%m%d")
                    if file_date < (datetime.now() - timedelta(days=1)):
                        R.lrem('livemail', -2, json.dumps(json_dict))
                except Exception:
                    print("error:")
    except Exception:
        pass

# task_kwargs = json.loads(json_dict['headers']['kwargsrepr'].replace("'", '"'))

# remove from Redis old communication tasks
R = redis.Redis(host=ecips_config.CELERY_BACKEND.split(":")[1].replace("//", ""))
search_json_list = list(set(R.lrange("communication", 0, -1)))
newjsonlist = [json.loads(ele.decode("utf-8")) for ele in search_json_list]
for json_dict in newjsonlist:
    task_name = json_dict['headers']['task']
    task_id = json_dict['headers']['id']
    task_kwargs = json.loads(json_dict['headers']['kwargsrepr'].replace("'", '"'))
    if 'prlm' in task_name:
        R.lrem('communication', -2, json.dumps(json_dict))
        print(task_id)

search_json_list = list(set(R.lrange("communication-prlm", 0, -1)))
newjsonlist = [json.loads(ele.decode("utf-8")) for ele in search_json_list]
for json_dict in newjsonlist:
    task_name = json_dict['headers']['task']
    task_id = json_dict['headers']['id']
    task_kwargs = json.loads(json_dict['headers']['kwargsrepr'].replace("'", '"'))
    prlm_file = task_kwargs['prlm_file']
    if 'prlm' in task_name:
        prlm_date = datetime.strptime(prlm_file.split("/")[3], "%Y-%m-%d")
        if prlm_date < (datetime.now() - timedelta(days=1)):
            R.lrem('communication-prlm', -2, json.dumps(json_dict))
        print(task_id)

# Revoke Reserved

for key_id in i.reserved().keys():
    if 'comms' in key_id:
        print(key_id)
        for task_dict in i.reserved()[key_id]:
            routing_key = task_dict['delivery_info']['routing_key']
            task_id = task_dict['id']
            task_name = task_dict['name']
            if routing_key == 'communication':
                if task_name == 'ecips_tasks.tasks_comms.process_prlm':
                    prlm_file = task_dict['kwargs']['prlm_file']
                    app.control.revoke(task_id, terminate=True)
                    print(f"comms channel {prlm_file}")
                    print(task_dict)
            else:
                if task_name == 'ecips_tasks.tasks_comms.process_prlm':
                    prlm_file = task_dict['kwargs']['prlm_file']
                    if True:
                        prlm_date = datetime.strptime(prlm_file.split("/")[3], "%Y-%m-%d")
                        if prlm_date < (datetime.now() - timedelta(days=1)):
                            app.control.revoke(task_id, terminate=True)
                            print(f"comms-prlm channel {prlm_file}")
# revoke from active
keys_deleted_total = 0
for idx in range(1):
    keys_deleted_round = 0
    for key_id in i.active().keys():
        if 'comms' in key_id:
            for task_dict in i.active()[key_id]:
                routing_key = task_dict['delivery_info']['routing_key']
                task_id = task_dict['id']
                task_name = task_dict['name']
                if routing_key == 'communication':
                    if task_name == 'ecips_tasks.tasks_comms.process_prlm':
                        app.control.revoke(task_id, terminate=True)
                        prlm_file = task_dict['kwargs']['prlm_file']
                        print(f"comms active channel {prlm_file}")
                        keys_deleted_round += 1
                else:
                    if task_name == 'ecips_tasks.tasks_comms.process_prlm':
                        prlm_file = task_dict['kwargs']['prlm_file']
                        try:
                            prlm_date = datetime.strptime(prlm_file.split("/")[3], "%Y-%m-%d")
                            if prlm_date < (datetime.now() - timedelta(days=1)):
                                app.control.revoke(task_id, terminate=True)
                                keys_deleted_round += 1
                                print(f"comms-prlm active channel {prlm_file}")
                        except Exception:
                            print("bad prlm process:")
    print(f"round {idx}: Keys_deleted = {keys_deleted_round}")
    keys_deleted_total += keys_deleted_round
    print(f"round {idx}: Keys_deleted total = {keys_deleted_total}")

# removing reserved
# removing active
