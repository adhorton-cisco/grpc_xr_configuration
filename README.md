## Telemetry Configuration using gRPC for Cisco IOS-XR in Python
**README OUT OF DATE**
This module contains a library with methods that are available to use over gRPC with IOS-XR boxes after 6.0.0. The API has several methods which allows a user to send simple commands to configure telemetry on an IOS-XR box. It abstracts away some of the complexities of the IOS-XR CLI or the iosxr_grpc tool found [here](https://github.com/cisco-ie/ios-xr-grpc-python). It also comes with a user-friendly menu to help configure the router with minimal programming experience required.

If you find any problems or need help, create an issue or contact me directly at adhorton@cisco.com

## Installation
1. Clone this repository into your project directory
```sh
git clone https://github.com/adhorton-cisco/ios_xr_telemetry_configuration.git
```
2. Create your virtual environment
3. Ensure that all dependencies are installed
```sh
pip install -r requirements.txt
```
The source files for iosxr_grpc are included in the repository because there is currently a version issue that prevents it being installed with pip. This repository will be modified in the future if the issue is resolved

4. Enable gRPC after you SSH into the router
```
grpc
 port 57777
 no-tls
 !
!
```

## Usage
Access the user-friendly menu by running telemetry_menu.py

If you would like to use the methods directly from the module, check the sample below.
This sample configuration can also be found in telemetry_menu.py
```
from config_telemetry import TelemetryConfig
config = TelemetryConfig('1.2.3.4', 57777, 10, 'user', 'password')

dg = TelemetryConfig.Destination_Group('DGroup1')
dg.add_destination('1.1.1.1', 57500, 'self-describing-gpb', 'grpc')
dg.add_destination('2.2.2.2', 57500, 'self-describing-gpb', 'grpc')
config.configure_destination_group(dg)

sg = TelemetryConfig.Sensor_Group('SGroup1')
sg.add_sensor_path('Cisco-IOS-XR-nto-misc-oper:memory-summary/nodes/node/summary')
sg.add_sensor_path('Cisco-IOS-XR-nto-misc-oper:memory-summary/nodes/node/detail')
config.configure_sensor_group(sg)

sub = TelemetryConfig.Subscription('Sub1', dg, sg, 30000)
config.configure_subscription(sub)

print(config.get_config())
```

## Useful Links

If you would like to test this all out with IOS-XRv, use the following link to request access to the vagrant box.

https://xrdocs.github.io/

## Contributors/Contact
* Adam Horton - adhorton@cisco.com

Project Link: [https://github.com/adhorton-cisco/ios_xr_telemetry_configuration](https://github.com/adhorton-cisco/ios_xr_telemetry_configuration)
