import json
from urllib import response
from grpc.framework.interfaces.face.face import AbortionError
import sys
import iosxr_grpc
sys.path.insert(0, '../')
from iosxr_grpc.cisco_grpc_client import CiscoGRPCClient

class MDT:
    def __init__(self, host, port, timeout, user, password):
        self._client = CiscoGRPCClient(host, port, timeout, user, password)

    def __str__(self):
        return self._client.getconfig('{"Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": [null]}')[1]

    def get_config(self):
        return json.loads(self._client.getconfig('{"Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": [null]}')[1])

    def create_destination_group(self, id, address, port, encoding, protocol):
        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "destination-groups": {
                    "destination-group": [
                        {
                            "destination-id": id,
                            "ipv4-destinations": {
                                "ipv4-destination": [
                                    {
                                        "ipv4-address": address,
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

        response = self._client.replaceconfig(json.dumps(request))
        return response

    def read_destination_group(self, name):
        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "destination-groups":{
                    "destination-group": [{
                        "destination-id": name
                    }]
                }
            }
        }
        try:
            return json.loads(self._client.getconfig(json.dumps(request))[1])
        except json.JSONDecodeError:
            return None

    def delete_destination_group(self, name):
        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "destination-groups":{
                    "destination-group": [{
                        "destination-id": name
                    }]
                }
            }
        }
        response = self._client.deleteconfig(json.dumps(request))
        return response

    def create_sensor_group(self, name, sensor_path):
        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "sensor-groups": {
                    "sensor-group": [
                        {
                            "sensor-group-identifier": name,
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

        response = self._client.replaceconfig(json.dumps(request))
        return response

    def read_sensor_group(self, name):
        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "sensor-groups":{
                    "sensor-group": [{
                        "sensor-group-identifier": name
                    }]
                }
            }
        }
        try:
            return json.loads(self._client.getconfig(json.dumps(request))[1])
        except json.JSONDecodeError:
            return None

    def delete_sensor_group(self, name):
        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "sensor-groups":{
                    "sensor-group": [{
                        "sensor-group-identifier": name
                    }]
                }
            }
        }
        response = self._client.deleteconfig(json.dumps(request))
        return response

    def create_subscription(self, name, sensor_group, destination_group, interval):
        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "subscriptions": {
                    "subscription": [
                        {
                            "subscription-identifier": name,
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

        response = self._client.replaceconfig(json.dumps(request))
        return response

    def read_subscription(self, name):
        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "subscriptions": {
                    "subscription": [
                        {
                            "subscription-identifier": name,
                        }
                    ]
                }
            }
        }

        response = json.loads(self._client.getconfig(json.dumps(request))[1])
        return response

    def delete_subscription(self, name):
        request = {
            "Cisco-IOS-XR-telemetry-model-driven-cfg:telemetry-model-driven": {
                "subscriptions": {
                    "subscription": [
                        {
                            "subscription-identifier": name,
                        }
                    ]
                }
            }
        }

        response = self._client.deleteconfig(json.dumps(request))
        return response

if __name__ == "__main__":
    bob = MDT("172.26.228.250", 61831, 10, "cisco", "cisco123")