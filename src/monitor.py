from re import L
from gnmi_config import MDT
import yaml
import os
import sys
import json
import logging
import logging.handlers
import signal
from cerberus import Validator
from grpc import FutureTimeoutError

#################### LOGGING ####################

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

logFile = 'app.log'

file_handler = logging.handlers.RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, backupCount=1)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logging.getLogger('pygnmi').setLevel(logging.CRITICAL)

#################################################

DELAY = 10
LOCAL_IP = "127.0.0.1"
CONFIG_PATH = "../config/config.yaml"

try:
    config = yaml.load(open(os.path.join(os.path.dirname(__file__), CONFIG_PATH), "r"), Loader=yaml.Loader)
    logger.info('config.yaml found')
except FileNotFoundError as err:
    logger.error('config.yaml could not be found')
    logger.debug('check location of config.yaml and mounting directory')
    raise err

def validate_config():
    """
        Validates the config.yaml file against the mandated schema
    """

    with open("schema.json") as f:
        schema = json.load(f)
    
    v = Validator(schema)
    if not v.validate(config):
        logger.error('config.yaml is formatted improperly')
        for error in v.errors.items():
            logger.debug(str(error))
        raise RuntimeError("config.yaml formatted improperly")
    logger.info('config.yaml read successfully')


def setup():
    """
        Creates a destination group for each collector in config.yaml
        Creates all sensor groups defined in config.yaml
    """

    try:
        router = config["router"]
        with MDT(LOCAL_IP, router["port"], router["username"], router["password"]) as router_config:

            for collector in config["collectors"]:
                dg = collector["destination-group"]
                router_config.create_destination(dg["destination-id"], dg["ip"], dg["port"], dg["encoding"], dg["protocol"])

                logger.info('Created Destination Group: ' + dg["destination-id"])

            for sensor_group in config["sensor-groups"]:
                for sensor_path in sensor_group["sensor-paths"]:
                    router_config.create_sensor_path(sensor_group["sensor-group-id"], sensor_path)

                logger.info('Created Sensor Group: ' + sensor_group["sensor-group-id"])

    except FutureTimeoutError as err:
        logger.error('Failed to connect to host')
        logger.debug('Check grpc configuration on host or username/password in config.yaml')
        raise err

    logger.info('Setup Successful')

def clean():
    """
        Removes all associated Destination Groups, Sensor Groups, and Subscriptions
    """

    router = config["router"]
    with MDT(LOCAL_IP, router["port"], router["username"], router["password"]) as router_config:
        for sensor_group in config["sensor-groups"]:
            router_config.delete_sensor_group(sensor_group["sensor-group-id"])
            logger.info("Removed Sensor Group: " + sensor_group["sensor-group-id"])
        
        for collector in config["collectors"]:
            router_config.delete_subscription(collector["subscription"]["subscription-id"])
            logger.info("Removed Subscription: " + collector["subscription"]["subscription-id"])
            router_config.delete_destination_group(collector["destination-group"]["destination-id"])
            logger.info("Removed Destination Group: " + collector["destination-group"]["destination-id"])

def check():
    """
        Checks connectivity to collectors in config.yaml and updates router telemetry configuration to highest priority
        
        :return: The index of the current active collector in the priority list
        :rtyp: int 
    """

    try:
        router = config["router"]
        with MDT(LOCAL_IP, router["port"], router["username"], router["password"]) as router_config:

            for collector in config["collectors"]:
                # If the collector does not yet have a subscription, create it
                if router_config.read_subscription(collector["subscription"]["subscription-id"]) == None:
                    for sensor_group in config["sensor-groups"]:
                        router_config.create_subscription(collector["subscription"]["subscription-id"], sensor_group["sensor-group-id"], collector["destination-group"]["destination-id"], collector["subscription"]["interval"])

                # Check the state of the subscription, if it is active, delete all subsequent subscriptions
                if router_config.check_connection(collector["subscription"]["subscription-id"]):
                    logger.info('Currently Streaming to: ' + collector["subscription"]["subscription-id"])
                    index = config["collectors"].index(collector)
                    for backup in config["collectors"][index + 1:]:
                        if router_config.read_subscription(backup["subscription"]["subscription-id"]) != None:
                            router_config.delete_subscription(backup["subscription"]["subscription-id"])
                    return index
    except FutureTimeoutError as err:
        logger.error('Failed to connect to host')
        logger.debug('Check grpc configuration on host or username/password in config.yaml')
        raise err
        
    logger.warning('NO ACTIVE COLLECTORS')
    return -1

if __name__ == "__main__":
    validate_config()
    setup()
    
    while True:
        collector = check()
        if collector == -1:
            if signal.sigtimedwait([signal.SIGTERM], DELAY) != None:
                break
        else:
            if signal.sigtimedwait([signal.SIGTERM], config["collectors"][collector]["subscription"]["interval"]/1000) != None:
                break

    clean()
    logger.info('Exited Successfully')