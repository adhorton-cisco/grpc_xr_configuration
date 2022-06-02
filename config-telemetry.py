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

        self.client = CiscoGRPCClient(host, port, timeout, user, password)

    def create_destination_group(self, name, ip, port, encoding, protocol):
        """ Configures a new destination-group

            :param name: The name of the new destination-group
            :type name: int
            :param ip: The ip address for the collector
            :type ip: str
            :param port: The port for the collector
            :type port: int
            :param encoding: The encoding to use for telemetry data
            :type encoding: str
            :param protocol: The protocol to use for transmitting telemetry data
            :type protocol: str
            :return: Return the response object
            :rtype: str
        """

        configuration = (
            'telemetry model-driven\n'
            ' destination-group ' + name + '\n'
            '  address-family ipv4 ' + ip + ' port ' + str(port) +'\n'
            '   encoding ' + encoding +'\n'
            '   protocol ' + protocol + '\n'
            '   !\n'
            '  !\n'
            '!\n'
        )
        response = self.client.cliconfig(configuration)
        return response

    def create_sensor_group(self, name, sensor_paths):
        """ Configures a new sensor-group

            :param name: The name of the new sensor-group
            :type name: str
            :param sensor_paths: The YANG models to stream
            :type sensor_paths: list
            :return: Return the response object
            :rtype: str
        """

        configuration = (
            'telemetry model-driven\n'
            ' sensor-group ' + name + '\n'
        )
        for sensor_path in sensor_paths:
            configuration += '  sensor-path ' + sensor_path + '\n'
        configuration += (
            ' !\n'
            '!'
        )
        response = self.client.cliconfig(configuration)
        return response
    
    def create_subscription(self, name, sensor_group, interval, destination_group):
        """ Configures a new subscription

            :param name: The name of the new subscription
            :type name: str
            :param sensor_group: The name of the sensor-group to subscribe to
            :type sensor_group: str
            :param interval: The streaming interval in milliseconds
            :type interval: int
            :param destination_group: The name of the destination-group to send telemetry data to
            :type destination_group: str
            :return: Return the response object
            :rtype: str
        """

        configuration = (
            'telemetry model-driven\n'
            ' subscription ' + name + '\n'
            '  sensor-group-id ' + sensor_group + ' sample-interval ' + str(interval) + '\n'
            '  destination-id ' + destination_group + '\n'
            '  !\n'
            ' !\n'
            '!'
        )
        response = self.client.cliconfig(configuration)
        return response
