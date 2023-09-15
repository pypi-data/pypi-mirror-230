import json
import redis
import subprocess
from ecips_utils import ecips_config

# Redis
R = redis.Redis(host=ecips_config.CELERY_BACKEND.split(':')[1].replace("//", ""))


def mem_utilization(directory_path):
    '''
    This function performs a memory health check for the sites filesystem

    Input:
        directory_path - directory path
    Output:
        mem_usage - percent mem utilization of the directory
    '''
    directory = directory_path.split('/')[-2]
    mem_usage = subprocess.Popen(['df', '-h', directory_path, '--output=pcent'], stdout=subprocess.PIPE)
    mem_usage = subprocess.run(['sed', '-n', '2p'], stdout=subprocess.PIPE, stdin=mem_usage.stdout)
    mem_usage = mem_usage.stdout.decode('utf-8')
    mem_usage = mem_usage.replace(' ', '')
    mem_usage = mem_usage.replace('%\n', '')
    records = {
        'per_mem_usage': mem_usage
    }
    R.setex(f"system-health:{directory}", 60*60, json.dumps(records))
    return mem_usage


def health_check(name=None, records=None):
    '''
    This function performs the application health check.

    Inputs:
        name - container name
    '''
    if records is None:
        R.setex(f"application-health:{name}", 5*60, "alive")
    else:
        R.setex(f"application-health:{name}", 5*60, json.dumps(records))
