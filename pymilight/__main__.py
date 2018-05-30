import argparse
import json
import logging
import queue
import threading
import time

from pymilight.milight_control import MiLightController
from pymilight.mqtt_client import MqttClient


def get_parser():
    parser = argparse.ArgumentParser(description="pymilight controller")
    parser.add_argument("--config", "-c", 
                        help="Path to config file", 
                        default="config.json")
    return parser


def main(args=None):
    if args is None:
        args = get_parser().parse_args()

    try:
        config = json.load(open(args.config))
    except (OSError, ValueError) as err:
        print("Error reading config from: %s" % args.config)
        print()
        print(err)
        return False
        
    logging.basicConfig(level=logging.DEBUG)

    inbound = queue.Queue()
    outbound = queue.Queue()
    shutdown = threading.Event()

    def mqtt_to_queue(device_type, device_id, group_id, msg):
        inbound.put((device_type, device_id, group_id, msg))

    mqtt_client = MqttClient(config, mqtt_to_queue)

    controller = MiLightController(inbound, outbound, shutdown)
    controller.start()

    while True:
        key = input("Press q to quit:")
        if key.lower().startswith("q"):
            shutdown.set()
            controller.join()
            break
        time.sleep(1)


if __name__ == '__main__':
    main()