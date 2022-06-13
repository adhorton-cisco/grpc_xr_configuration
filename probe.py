from subprocess import run
from yang_config import MDT
from yaml import load, Loader, dump, Dumper


TIMEOUT = 10
config = load(open("config.yaml", "r"), Loader=Loader)

def setup():
    """
        Creates a destination group for each collector in config.yaml
        Creates all sensor groups defined in config.yaml
        Creates a subscription of all sensor-groups to the first collector
    """
    router = config["router"]
    router_config = MDT(router["ip"], router["port"], TIMEOUT, router["username"], router["password"])

    for collector in config["collectors"]:
        dg = collector["destination-group"]
        router_config.create_destination(dg["destination-id"], dg["ip"], dg["port"], dg["encoding"], dg["protocol"])
    
    primary = config["collectors"][0]
    for sensor_group in config["sensor-groups"]:
        for sensor_path in sensor_group["sensor-paths"]:
            router_config.create_sensor_path(sensor_group["sensor-group-id"], sensor_path)
        router_config.create_subscription(primary["subscription"]["subscription-id"], sensor_group["sensor-group-id"], primary["destination-group"]["destination-id"], primary["subscription"]["interval"])   
    

def ping(host):
    """ Pings a host on the network
    
        :param host: The ip address to ping
        :type host: str
        :return: Whether or not the host replied
        :rtype: bool
    """

    command = ["ping", "-c", "1", host]
    return run(command).returncode == 0

def main():
    """
        Pings collectors in config.yaml and updates router telemetry configuration to highest priority
    """
    router = config["router"]
    router_config = MDT(router["ip"], router["port"], TIMEOUT, router["username"], router["password"])

    for collector in config["collectors"]:
        if ping(collector["destination-group"]["ip"]):
            if router_config.read_subscription(collector["subscription"]["subscription-id"]) != "":
                break
            else:
                index = config["collectors"].index(collector)
                for backup in config["collectors"][index + 1:]:
                    if router_config.read_subscription(backup["subscription"]["subscription-id"]) != "":
                        router_config.delete_subscription(backup["subscription"]["subscription-id"])
                for sensor_group in config["sensor-groups"]:
                    router_config.create_subscription(collector["subscription"]["subscription-id"], sensor_group["sensor-group-id"], collector["destination-group"]["destination-id"], collector["subscription"]["interval"])
                break