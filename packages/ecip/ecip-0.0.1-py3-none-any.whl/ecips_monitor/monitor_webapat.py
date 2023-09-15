from ecips_utils import ecips_config, ecips_health
# import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import requests
import redis
import json

# Define action to do on detection of moved .png
# (RSYNC Creates TMP file and last action is a move command to the final name)


def create_webapat_event_handler(
  patterns=ecips_config.ECIPS_WEBAPAT_FILE_EXTENSION_PATTERN,
  ignore_patterns=ecips_config.ECIPS_MPE_FILE_IGNORE_PATTERN,
  ignore_directories=False,
  case_sensitive=True
):

    webapat_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    def on_moved(event):
        logging.debug(f"Processing moved {event.dest_path}")
        payload = {"file_path": event.dest_path}  # TODO enable mpe specific processing based on folder

        requests.post('{ecips_controller_endpoint}/SearchImage'.format(
            ecips_controller_endpoint=ecips_config.ECIPS_CONTROLLER_ADDRESS),
                          data=json.dumps(payload))

    def on_created(event):
        logging.debug(f"Processing created {event.src_path}")
        payload = {"file_path": event.src_path}  # TODO enable mpe specific processing based on folder

        requests.post('{ecips_controller_endpoint}/SearchImage'.format(
            ecips_controller_endpoint=ecips_config.ECIPS_CONTROLLER_ADDRESS),
                          data=json.dumps(payload))

    def on_deleted(event):
        logging.debug(f"Someone deleted {event.src_path}!")

    def on_modified(event):
        logging.debug(f"Processing modified {event.dest_path}")
        payload = {"file_path": event.dest_path}  # TODO enable mpe specific processing based on folder

        requests.post('{ecips_controller_endpoint}/SearchImage'.format(
            ecips_controller_endpoint=ecips_config.ECIPS_CONTROLLER_ADDRESS),
                          data=json.dumps(payload))

    webapat_event_handler.on_created = on_created
    webapat_event_handler.on_deleted = on_deleted
    webapat_event_handler.on_modified = on_modified
    webapat_event_handler.on_moved = on_moved

    return webapat_event_handler


def create_webapat_monitoring(path_to_monitor=ecips_config.ECIPS_WEBAPAT_LANDING_ZONE_PATH,
                              webapat_event_handler=create_webapat_event_handler(),
                              go_recursively=True):
    """
    This Function creates a python watchdog observer:
    Parameters:
    path_to_monitor (str): path to folder to monitor
    Returns:
     webapat observer
    """

    webapat_observer = Observer()
    webapat_observer.schedule(webapat_event_handler, path_to_monitor, recursive=go_recursively)

    return webapat_observer


if __name__ == '__main__':
    """
    This Call creates a python watchdog :
    Parameters:
    path_to_monitor (str): path to folder to monitor
    Returns:
     webapat observer
    """
    R = redis.Redis(host=ecips_config.CELERY_BACKEND.split(':')[1].replace("//", ""))
    logging.basicConfig(format='%(asctime)s %(message)s', level=ecips_config.LOGGING_LEVEL)  # NO SONAR
    # - Logs going to local Docker container and require server
    # access with access to said Docker container files to access.
    logging.getLogger(__name__)
    logging.debug("Starting webapat monitoring for {}".format(ecips_config.ECIPS_MPE_LANDING_ZONE_PATH))
    webapat_observer = create_webapat_monitoring(path_to_monitor=ecips_config.ECIPS_WEBAPAT_LANDING_ZONE_PATH,
                                                 webapat_event_handler=create_webapat_event_handler(),
                                                 go_recursively=True)

    webapat_observer.start()

    while True:
        time.sleep(1)
        ecips_health.health_check(name='monitor_webapat')
