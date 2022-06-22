from yang_config import MDT
from yaml import load, Loader
import os

def cleanup():
    """
        Removes all associated Destination Groups, Sensor Groups, and Subscriptions
    """

    TIMEOUT = 10
    config_path = "../config/config.yaml"
    config = load(open(os.path.join(os.path.dirname(__file__), config_path), "r"), Loader=Loader)

    router = config["router"]
    router_config = MDT(router["ip"], router["port"], TIMEOUT, router["username"], router["password"])

    for sensor_group in config["sensor-groups"]:
        router_config.delete_sensor_group(sensor_group["sensor-group-id"])
        print("Removed ", sensor_group["sensor-group-id"])
    
    for collector in config["collectors"]:
        router_config.delete_subscription(collector["subscription"]["subscription-id"])
        print("Removed ", collector["subscription"]["subscription-id"])
        router_config.delete_destination_group(collector["destination-group"]["destination-id"])
        print("Removed ", collector["destination-group"]["destination-id"])

    print(router_config.get_config())

if __name__ == "__main__":
    cleanup()