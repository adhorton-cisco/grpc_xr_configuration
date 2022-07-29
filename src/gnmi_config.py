from pygnmi.client import gNMIclient

class MDT:
    def __init__(self, host, port, user, password, path_cert=None):
        """ Constructor Method

            :param host: The ip address for the device
            :type host: str
            :param port: The port for the device
            :type port: int
            :param user: Username for device login
            :type user: str
            :param password: Password for device login
            :type password: str
            :param path_cert: Path to certificate for a secure TLS connection
            :type password: str, optional
        """
        if path_cert == None:
            self._client = gNMIclient(target=(host, port), username=user, password=password, insecure=True)
        else:
            self._client = gNMIclient(target=(host, port), username=user, password=password, path_cert=path_cert, override="ems.cisco.com")
        self._client.connect()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._client.close()

    def get_capabilities(self):
        """ Gets the capabilities of the target device

            :return: The gNMI Response
            :type: dict
        """

        return self._client.capabilities()

    def get_config(self):
        """ Gets the current telemetry configuration in JSON format

            :return: The gNMI Notification
            :rtype: dict
        """

        return self._client.get(path=['Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven'], encoding='json_ietf')

    ########## Destination Groups ##########

    def create_destination(self, destination_group, ip, port, encoding, protocol, tls, tls_hostname=None):
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
            :param tls: Whether or not communication uses tls
            :type tls: bool
            :param tls_hostname: Hostname to use for tls communication. Only valid when tls is true
            :type tls_hostname: str, optional
            :return: The gNMI Response
            :rtype: dict
        """

        protocol_dict = {"protocol": protocol}

        if not tls:
            protocol_dict["no-tls"] = None
        elif tls_hostname != None:
            protocol_dict["tls-hostname"] = tls_hostname

        request = [
            (
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven",
            
            {
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
                                        "protocol": protocol_dict
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        )
        ]

        response = self._client.set(update=request, encoding='json_ietf')
        return response

    def read_destination_group(self, destination_group):
        """ Reads the configuration of a specific destination group
        
            :param destination_group: Name of the destination group
            :type destination_group: str
            :return: The gNMI Notification
            :rtype: dict
        """

        request = 'Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven/destination-groups/destination-group[destination-id={}]'.format('"' + destination_group + '"')
        return self._client.get(path=[request], encoding='json_ietf')

    def read_all_destination_groups(self):
        """ Reads the configuration of all destination groups

            :return: The gNMI Notification
            :rtype: dict
        """

        request = 'Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven/destination-groups'
        response = self._client.get(path=[request], encoding='json_ietf')
        return response
    
    def delete_destination_group(self, destination_group):
        """ Deletes the configuration of a specific destination group
        
            :param destination_group: Name of the destination group
            :type destination_group: str
            :return: The gNMI Response
            :rtype: dict
        """

        request = 'Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven/destination-groups/destination-group[destination-id={}]'.format('"' + destination_group + '"')
        response = self._client.set(delete=[request], encoding='json_ietf')
        return response

    ########## Sensor Groups ##########

    def create_sensor_path(self, sensor_group, sensor_path):
        """ Creates a new sensor group with the sensor path, or adds the sensor path to an existing group (if name of group matches an existing group)
        
            :param sensor_group: The name of the sensor group
            :type sensor_group: str
            :param sensor_path: The name of the sensor path
            :type sensor_path: str
            :return: The gNMI Response
            :rtype: dict
        """

        request = [
            (
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven",

            {
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
        )
        ]

        response = self._client.set(update=request, encoding='json_ietf')
        return response

    def read_sensor_group(self, sensor_group):
        """ Reads the configuration of a specific sensor group
        
            :param sensor_group: The name of the sensor group
            :type sensor_group: str
            :return: The gNMI Notification
            :rtype: dict
        """

        request = 'Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven/sensor-groups/sensor-group[sensor-group-identifier={}]'.format('"' + sensor_group + '"')
        return self._client.get(path=[request], encoding='json_ietf')

    def read_all_sensor_groups(self):
        """ Reads the configuration of all sensor groups
        
            :return: The gNMI Notification
            :rtype: dict
        """

        request = 'Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven/sensor-groups'
        return self._client.get(path=[request], encoding='json_ietf')

    def delete_sensor_group(self, sensor_group):
        """ Deletes the configuration of a specific sensor group
        
            :param sensor_group: The name of the sensor_group
            :type sensor_group: str
            :return: The gNMI Response
            :rtype: dict
        """

        request = 'Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven/sensor-groups/sensor-group[sensor-group-identifier={}]'.format('"' + sensor_group + '"')
        response = self._client.set(delete=[request], encoding='json_ietf')
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
            :return: The gNMI Response
            :rtype: dict
        """

        request = [
            (
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven",
            
            {
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
        )
        ]

        response = self._client.set(update=request, encoding='json_ietf')
        return response

    def read_subscription(self, subscription):
        """ Read the configuration of a specified subscription
        
            :param subscription: The name of the subscription
            :type subscription: str
            :return: The gNMI Notification
            :rtype: dict
        """

        request = 'Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven/subscriptions/subscription[subscription-identifier={}]'.format('"' + subscription + '"')
        response = self._client.get(path=[request], encoding='json_ietf')
        return response

    def read_all_subscriptions(self):
        """ Reads the configuration of all subscriptions
        
            :return: The gNMI Notification
            :rtype: dict
        """

        request = 'Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven/subscriptions'
        response = self._client.get(path=[request], encoding='json_ietf')
        return response

    def delete_subscription(self, subscription):
        """ Deletes the specified subscription
        
            :param subscription:
            :type subscription: str
            :return: The gNMI Response
            :rtype: dict
        """

        request = 'Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven/subscriptions/subscription[subscription-identifier={}]'.format('"' + subscription + '"')
        response = self._client.set(delete=[request], encoding='json_ietf')
        return response

    def check_connection(self, subscription):
        """ Checks telemetric connection to a host on the network
        
            :param subscription: The subscription to check
            :type subscription: str
            :return: Whether or not the subscription is active
            :rtype: bool
        """

        request = 'Cisco-IOS-XR-telemetry-model-driven-oper:telemetry-model-driven/subscriptions/subscription[subscription-id={}]/subscription'.format('"' + subscription + '"')
        response = self._client.get(path=[request], encoding='json_ietf')
        return response["notification"][0]["update"][0]["val"]["state"] == "active"