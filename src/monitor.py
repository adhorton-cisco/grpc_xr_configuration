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

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(log_formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

logging.getLogger('pygnmi').setLevel(logging.CRITICAL)

#################################################

def validate_config(config, schema):
    """
        Validates the config.yaml file against the mandated schema
    """
    
    v = Validator(schema)
    if not v.validate(config):
        logger.error('config.yaml is formatted improperly')
        for error in v.errors.items():
            logger.debug(str(error))
        raise RuntimeError("config.yaml formatted improperly")
    logger.info('config.yaml read successfully')

    return True

def setup(config):
    """
        Creates a destination group for each collector in config.yaml
        Creates all sensor groups defined in config.yaml
    """

    try:
        router = config["router"]

        if router["tls"]:
            path_cert = "/config/ems.pem"
        else:
            path_cert = None
    
        with MDT(router["ip"], router["port"], router["username"], router["password"], path_cert=path_cert) as router_config:

            for collector in config["collectors"]:
                dg = collector["destination-group"]
                tls_hostname = dg["tls-hostname"] if "tls-hostname" in dg else None
                router_config.create_destination(dg["destination-id"], dg["ip"], dg["port"], dg["encoding"], dg["protocol"], dg["tls"], tls_hostname)

                logger.info('Created Destination Group: ' + dg["destination-id"])

            for sensor_group in config["sensor-groups"]:
                for sensor_path in sensor_group["sensor-paths"]:
                    router_config.create_sensor_path(sensor_group["sensor-group-id"], sensor_path)

                logger.info('Created Sensor Group: ' + sensor_group["sensor-group-id"])

    except FutureTimeoutError as err:
        logger.error('Failed to connect to host')
        logger.debug('Check grpc configuration on host or username/password in config.yaml')
        raise err
    except Exception as err:
        logger.error('Failed to find ems.pem')
        logger.debug('Check to see if ems.pem is in config directory mounted in container')
        raise err

    logger.info('Setup Successful')

def clean(config):
    """
        Removes all associated Destination Groups, Sensor Groups, and Subscriptions
    """

    try:
        router = config["router"]

        if router["tls"]:
            path_cert = "/config/ems.pem"
        else:
            path_cert = None

        with MDT(router["ip"], router["port"], router["username"], router["password"], path_cert=path_cert) as router_config:
            for sensor_group in config["sensor-groups"]:
                router_config.delete_sensor_group(sensor_group["sensor-group-id"])
                logger.info("Removed Sensor Group: " + sensor_group["sensor-group-id"])
            
            for collector in config["collectors"]:
                if router_config.read_subscription(collector["subscription"]["subscription-id"]) != None:
                    router_config.delete_subscription(collector["subscription"]["subscription-id"])
                    logger.info("Removed Subscription: " + collector["subscription"]["subscription-id"])
                router_config.delete_destination_group(collector["destination-group"]["destination-id"])
                logger.info("Removed Destination Group: " + collector["destination-group"]["destination-id"])

    except FutureTimeoutError as err:
        logger.error('Failed to connect to host')
        logger.debug('Check grpc configuration on host or username/password in config.yaml')
        raise err
    except Exception as err:
        logger.error('Failed to find ems.pem')
        logger.debug('Check to see if ems.pem is in config directory mounted in container')
        raise err

def check(config):
    """
        Checks connectivity to collectors in config.yaml and updates router telemetry configuration to highest priority
        
        :return: The index of the current active collector in the priority list
        :rtype: int 
    """

    try:
        router = config["router"]

        if router["tls"]:
            path_cert = "/config/ems.pem"
        else:
            path_cert = None

        with MDT(router["ip"], router["port"], router["username"], router["password"], path_cert=path_cert) as router_config:

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
    except Exception as err:
        logger.error('Failed to find ems.pem')
        logger.debug('Check to see if ems.pem is in config directory mounted in container')
        raise err
        
    logger.warning('NO ACTIVE COLLECTORS')
    return -1

def main(config_path, schema_path):
    DELAY = 10

    try:
        with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
            config = yaml.load(config_file, Loader=yaml.Loader)
            logger.info('config.yaml found')
    except FileNotFoundError as err:
        logger.error('config.yaml could not be found')
        logger.debug('check location of config.yaml and mounting directory')
        raise err
    except yaml.YAMLError as err:
        logger.error('config.yaml is not a valid YAML file')
        raise err

    with open(os.path.join(os.path.dirname(__file__), schema_path)) as schema_file:
        schema = json.load(schema_file)

    validate_config(config, schema)
    setup(config)
    
    while True:
        collector = check(config)
        if collector == -1:
            if signal.sigtimedwait([signal.SIGTERM], DELAY) != None:
                break
        else:
            if signal.sigtimedwait([signal.SIGTERM], config["collectors"][collector]["subscription"]["interval"]/1000) != None:
                break

    clean(config)
    logger.info('Exited Successfully')

if __name__ == "__main__":
    CONFIG_PATH = "../config/config.yaml"
    SCHEMA_PATH = "./schema.json"
    main(CONFIG_PATH, SCHEMA_PATH)