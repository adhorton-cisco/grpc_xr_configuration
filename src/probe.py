from yang_config import MDT
from yaml import load, Loader
import os
import time


TIMEOUT = 10
config_path = "../config/config.yaml"
config = load(open(os.path.join(os.path.dirname(__file__), config_path), "r"), Loader=Loader)

def setup():
    """
        Creates a destination group for each collector in config.yaml
        Creates all sensor groups defined in config.yaml
    """
    router = config["router"]
    router_config = MDT(router["ip"], router["port"], TIMEOUT, router["username"], router["password"])

    for collector in config["collectors"]:
        dg = collector["destination-group"]
        router_config.create_destination(dg["destination-id"], dg["ip"], dg["port"], dg["encoding"], dg["protocol"])

    for sensor_group in config["sensor-groups"]:
        for sensor_path in sensor_group["sensor-paths"]:
            router_config.create_sensor_path(sensor_group["sensor-group-id"], sensor_path)

def check():
    """
        Checks connectivity to collectors in config.yaml and updates router telemetry configuration to highest priority
        
        :return: The index of the current active collector in the priority list
        :rtyp: int 
    """

    router = config["router"]
    router_config = MDT(router["ip"], router["port"], TIMEOUT, router["username"], router["password"])

    for collector in config["collectors"]:
        # If the collector does not yet have a subscription, create it
        if router_config.read_subscription(collector["subscription"]["subscription-id"]) == "":
            for sensor_group in config["sensor-groups"]:
                router_config.create_subscription(collector["subscription"]["subscription-id"], sensor_group["sensor-group-id"], collector["destination-group"]["destination-id"], collector["subscription"]["interval"])

        # Check the state of the subscription, if it is active, delete all subsequent subscriptions
        if router_config.check_connection(collector["subscription"]["subscription-id"]):
            index = config["collectors"].index(collector)
            for backup in config["collectors"][index + 1:]:
                if router_config.read_subscription(backup["subscription"]["subscription-id"]) != "":
                    router_config.delete_subscription(backup["subscription"]["subscription-id"])
            return index
        
    return -1
    

if __name__ == "__main__":
    setup()
    while True:
        collector = check()
        if collector == -1:
            print("NO COLLECTORS ACTIVE: ", time.ctime())
            time.sleep(15)
        else:
            time.sleep(config["collectors"][collector]["subscription"]["interval"]/1000)