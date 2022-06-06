import sys
sys.path.insert(0, '../')
from iosxr_grpc.cisco_grpc_client import CiscoGRPCClient


class TelemetryConfig:
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
    
    class Destination_Group:
        def __init__(self, name, destinations=None):
            """ Constructor Method
            
                :param name: The name of the destination group
                :type name: str
                :param destinations: A list of Destinations to add to the destination group
                :type destinations: list of TelemetryConfig.Destination_Group.Destination objects, optional
            """

            if destinations == None:
                destinations = []
            self.destinations = destinations
            self.name = name

        class Destination:
            def __init__(self, ip, port, encoding, protocol):
                """ Constructor Method
                
                    :param ip: The ip address of the destination
                    :type ip: str
                    :param port: The port of the destination
                    :type port: int
                    :param encoding: The encoding for the telemetry streaming
                    :type encoding: str
                    :param protocol: The protocol for telemetry streaming
                    :type protocol: str
                """

                self.ip = ip
                self.port = port
                self.encoding = encoding
                self.protocol = protocol
        
        def add_destination(self, ip, port, encoding, protocol):
            """ Add a destination to the group by specifying values

                :param ip: The ip address of the destination
                :type ip: str
                :param port: The port of the destination
                :type port: int
                :param encoding: The encoding for the telemetry streaming
                :type encoding: str
                :param protocol: The protocol for telemetry streaming
                :type protocol: str
                :return: The new Destination object
                :rtype: TelemetryConfig.Destination_Group.Destination
            """
            new_dest = TelemetryConfig.Destination_Group.Destination(ip, port, encoding, protocol)
            self.destinations.append(new_dest)
            return new_dest
        
        def add_destination_obj(self, destination):
            """ Add a destination to the group with a Destination object
            
                :param destination: The destination to add to the group
                :type destination: TelemetryConfig.Destination_Group.Destination
            """

            self.destinations.append(destination)
    
    class Sensor_Group:
        def __init__(self, name, sensor_paths=None):
            """ Constructor Method

                :param name: The name of the sensor group
                :type name: str
                :param sensor_paths: A list of sensor paths to add to the group
                :type sensor_paths: list of str, optional
            """

            if sensor_paths == None:
                sensor_paths = []
            self.name = name
            self.sensor_paths = sensor_paths

        def add_sensor_path(self, path):
            """ Adds a sensor path to the sensor group

                :param path: The sensor path to add to the group
                :type path: str
            """
            self.sensor_paths.append(path)

        def remove_sensor_path(self, path):
            """ Removes a sensor path from the sensor group

                :param path: The sensor path to remove
                :type path: str
            """
            try:
                self.sensor_paths.remove(path)
            except ValueError:
                print("Path not found in " + self.name)

    class Subscription:
        def __init__(self, name, sensor_group, destination_group, interval):
            """ Constructor Method

                :param name: The name of the subscription
                :type name: str
                :param sensor_group: The sensor group to configure the subscription with
                :type sensor_group: TelemetryConfig.Sensor_Group
                :param destination_group: The destination group of the subscription
                :type destination_group: TelemetryConfig.Destination_Group
                :param interval: The interval between telemetry streams in milliseconds
                :type interval: int
            """
            self.name = name
            self.sensor_group = sensor_group
            self.destination_group = destination_group
            self.interval = interval


    def create_destination_group(self, destination_group):
        """ Configures a new destination-group on the router

            :param destination_group: The destination group to configure
            :type destination_group: TelemetryConfig.Destination_Group
            :return: Return the response object
            :rtype: str
        """

        configuration = (
            'telemetry model-driven\n'
            ' destination-group ' + destination_group.name + '\n'
        )
        for destination in destination_group.destinations:
            configuration += (
                '  address-family ipv4 ' + destination.ip + ' port ' + str(destination.port) +'\n'
                '   encoding ' + destination.encoding +'\n'
                '   protocol ' + destination.protocol + '\n'
                '   !\n'
            )
        configuration += (
            '  !\n'
            '!\n'
        )
        response = self._client.cliconfig(configuration)
        return response

    def create_sensor_group(self, sensor_group):
        """ Configures a new sensor-group

            :param sensor_group: The sensor group to configure
            :type sensor_group: TelemetryConfig.Sensor_Group
            :return: Return the response object
            :rtype: str
        """

        configuration = (
            'telemetry model-driven\n'
            ' sensor-group ' + sensor_group.name + '\n'
        )
        for sensor_path in sensor_group.sensor_paths:
            configuration += '  sensor-path ' + sensor_path + '\n'
        configuration += (
            ' !\n'
            '!'
        )
        response = self._client.cliconfig(configuration)
        return response
    
    def create_subscription(self, subscription):
        """ Configures a new subscription

            :param subscription: The subscription to configure
            :type subscription: TelemetryConfig.Subscription
            :return: Return the response object
            :rtype: str
        """

        configuration = (
            'telemetry model-driven\n'
            ' subscription ' + subscription.name + '\n'
            '  sensor-group-id ' + subscription.sensor_group.name + ' sample-interval ' + str(subscription.interval) + '\n'
            '  destination-id ' + subscription.destination_group.name + '\n'
            '  !\n'
            ' !\n'
            '!'
        )
        response = self._client.cliconfig(configuration)
        return response

    def get_config(self):
        """ Returns a string containing the current telemetry configuration

            :return: The current telemetry configuration
            :rtype: str
        """
        return self._client.showcmdtextoutput('show running-config telemetry model-driven')[1]

    def delete_config(self, target=None):
        """ Clears some or all telemetry configurations. If target is not specified, telemetry configuration is erased entirely
        
            :param target: The target configuration to remove
            :type target: TelemetryConfig.Destination_Group, TelemetryConfig.Sensor_Group, TelemetryConfig.Subscription, optional
        """

        if target == None:
            configuration = 'no telemetry model-driven\n!'
            response = self._client.cliconfig(configuration)
            return response
        elif isinstance(target, TelemetryConfig.Destination_Group):
            configuration = (
            'telemetry model-driven\n'
            ' no destination-group ' + target.name + '\n'
            ' !\n'
            '!'
            )
            response = self._client.cliconfig(configuration)
            return response
        elif isinstance(target, TelemetryConfig.Sensor_Group):
            configuration = (
            'telemetry model-driven\n'
            ' no sensor-group ' + target.name + '\n'
            ' !\n'
            '!'
            )
            response = self._client.cliconfig(configuration)
            return response
        elif isinstance(target, TelemetryConfig.Subscription):
            configuration = configuration = (
            'telemetry model-driven\n'
            ' no subscription ' + target.name + '\n'
            ' !\n'
            '!'
            )
            response = self._client.cliconfig(configuration)
            return response
        else:
            return "Target not configurable"
