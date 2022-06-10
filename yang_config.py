import json
from iosxr_grpc.cisco_grpc_client import CiscoGRPCClient

class MDT:
    def __init__(self, host, port, timeout, user, password):
        """ Constructor Method

            :param host: The ip address for the device
            :type host: str
            :param port: The port for the device
            :type port: int
            :param timeout: How long before the rpc call timeout
            :type timeout: int
            :param user: Username for device login
            :type user: str
            :param password: Password for device login
            :type password: str
        """

        self._client = CiscoGRPCClient(host, port, timeout, user, password)

    def get_config(self):
        """ Gets the current telemetry configuration in JSON format

            :return: The current telemetry configuration in JSON
            :rtype: str
        """

        return self._client.getconfig('{"Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": [null]}')[1]

    ########## Destination Groups ##########

    def create_destination(self, destination_group, ip, port, encoding, protocol):
        """ Creates a new destination group, or adds a new destination to an existing group (if name matches the name of the existing group)
            Can also be used to modify attributes of a destination if name and ip match the name and ip of an exisiting group
        
            :param destination_group: Name of the destination group
            :type destination_group: str
            :param ip: IPv4 address of the destination
            :type ip: str
            :param port: Port of the destination
            :type port: int
            :param encoding: Encoding for transmission
            :type encoding: str
            :param protocol: Protocol for the transmission
            :type protocol: str
            :return: The Response object
            :rtype: Response object
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "destination-groups": {
                    "destination-group": [
                        {
                            "destination-id": destination_group,
                            "ipv4-destinations": {
                                "ipv4-destination": [
                                    {
                                        "ipv4-address": ip,
                                        "destination-port": port,
                                        "encoding": encoding,
                                        "protocol": {
                                            "protocol": protocol
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }

        response = self._client.mergeconfig(json.dumps(request))
        return response

    def read_destination_group(self, destination_group):
        """ Reads the configuration of a specific destination group
        
            :param destination_group: Name of the destination group
            :type destination_group: str
            :return: The destination group in JSON format
            :rtype: str
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "destination-groups":{
                    "destination-group": [{
                        "destination-id": destination_group
                    }]
                }
           
            }
        }
        return self._client.getconfig(json.dumps(request))[1]

    def read_all_destination_groups(self):
        """ Reads the configuration of all destination groups

            :return: All destination groups in JSON format
            :rtype: str
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "destination-groups":{
                    "destination-group": []
                }
            }
        }

        self._client.getconfig(json.dumps(request))[1]
    
    def delete_destination_group(self, destination_group):
        """ Deletes the configuration of a specific destination group
        
            :param destination_group: Name of the destination group
            :type destination_group: str
            :return: The Response object
            :rtype: Response object
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "destination-groups":{
                    "destination-group": [{
                        "destination-id": destination_group
                    }]
                }
            }
        }

        response = self._client.deleteconfig(json.dumps(request))
        return response

    ########## Sensor Groups ##########

    def create_sensor_path(self, sensor_group, sensor_path):
        """ Creates a new sensor group with the sensor path, or adds the sensor path to an existing group (if name of group matches an existing group)
        
            :param sensor_group: The name of the sensor group
            :type sensor_group: str
            :param sensor_path: The name of the sensor path
            :type sensor_path: str
            :return: The Response object
            :rtype: Response object
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "sensor-groups": {
                    "sensor-group": [
                        {
                            "sensor-group-identifier": sensor_group,
                            "sensor-paths": {
                                "sensor-path": [
                                    {
                                        "telemetry-sensor-path": sensor_path
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }

        response = self._client.mergeconfig(json.dumps(request))
        return response

    def read_sensor_group(self, sensor_group):
        """ Reads the configuration of a specific sensor group
        
            :param sensor_group: The name of the sensor group
            :type sensor_group: str
            :return: The sensor group in JSON format
            :rtype: str
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "sensor-groups":{
                    "sensor-group": [{
                        "sensor-group-identifier": sensor_group
                    }]
                }
            }
        }
        
        return self._client.getconfig(json.dumps(request))[1]

    def read_all_sensor_groups(self):
        """ Reads the configuration of all sensor groups
        
            :return: All sensor groups in JSON format
            :rtype: str
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "sensor-groups":{
                    "sensor-group": []
                }
            }
        }

        return self._client.getconfig(json.dumps(request))[1]

    def delete_sensor_group(self, sensor_group):
        """ Deletes the configuration of a specific sensor group
        
            :param sensor_group: The name of the sensor_group
            :type sensor_group: str
            :return: The Response object
            :rtype: Response object
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "sensor-groups":{
                    "sensor-group": [{
                        "sensor-group-identifier": sensor_group
                    }]
                }
            }
        }
        response = self._client.deleteconfig(json.dumps(request))
        return response

    ########## Subscriptions ##########

    def create_subscription(self, subscription, sensor_group, destination_group, interval):
        """ Creates or modifies an existing subscription. To modify a subscription, enter a name of an already existing subscription
        
            :param subscription: Name of subscription
            :type subscription: str
            :param sensor_group: Name of sensor group
            :type sensor_group: str
            :param destination_group: Name of destination group
            :type destination_group: str
            :param interval: The interval to stream data in milliseconds
            :type interval: int
            :return: The Response object
            :rtype: Response object
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "subscriptions": {
                    "subscription": [
                        {
                            "subscription-identifier": subscription,
                            "sensor-profiles": {
                                "sensor-profile": [
                                    {
                                        "sensorgroupid": sensor_group,
                                        "sample-interval": interval
                                    }
                                ]
                            },
                            "destination-profiles": {
                                "destination-profile": [
                                    {
                                        "destination-id": destination_group
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }

        response = self._client.mergeconfig(json.dumps(request))
        return response

    def read_subscription(self, subscription):
        """ Read the configuration of a specified subscription
        
            :param subscription:
            :type subscription: str
            :return: The subscription in JSON format
            :rtype: str
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "subscriptions": {
                    "subscription": [
                        {
                            "subscription-identifier": subscription,
                        }
                    ]
                }
            }
        }

        response = self._client.getconfig(json.dumps(request))[1]
        return response

    def read_all_subscriptions(self):
        """ Reads the configuration of all subscriptions
        
            :return: All subscriptions in JSON format
            :rtype: str
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "subscriptions": {
                    "subscription": []
                }
            }
        }

        response = self._client.getconfig(json.dumps(request))[1]
        return response

    def delete_subscription(self, subscription):
        """ Deletes the specified subscription
        
            :param subscription:
            :type subscription: str
            :return: The Response object
            :rtype: Response object
        """

        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "subscriptions": {
                    "subscription": [
                        {
                            "subscription-identifier": subscription,
                        }
                    ]
                }
            }
        }

        response = self._client.deleteconfig(json.dumps(request))
        return response