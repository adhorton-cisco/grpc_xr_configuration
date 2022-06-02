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
    
    class Destination:
        def __init__(self, ip, port, encoding, protocol):
            self.ip = ip
            self.port = port
            self.encoding = encoding
            self.protocol = protocol


    def create_destination_group(self, name, destinations):
        """ Configures a new destination-group

            :param name: The name of the new destination-group
            :type name: int
            :param destinations: A list of TelemetryConfig.Destination objects
            :type destinations: list
            :return: Return the response object
            :rtype: str
        """

        configuration = (
            'telemetry model-driven\n'
            ' destination-group ' + name + '\n'
        )
        for destination in destinations:
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
        response = self._client.cliconfig(configuration)
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
        response = self._client.cliconfig(configuration)
        return response

if __name__ == '__main__':
    print('A module for configuring model-driven telemetry')

    # SAMPLE CODE
    # configurer = TelemetryConfig('1.1.1.1', 57744, 10, 'cisco', 'cisco123')
    # collector1 = TelemetryConfig.Destination('2.2.2.2', 57500, 'self-describing-gpb', 'grpc')
    # configurer.create_destination_group('DGroup', [collector1])
    # configurer.create_sensor_group('SGroup', ['Cisco-IOS-XR-nto-misc-oper:memory-summary/nodes/node/summary'])
    # configurer.create_subscription('Sub', 'SGroup', 30000, 'DGroup')