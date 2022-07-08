import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
import pytest
import yaml
import json
from unittest.mock import Mock, MagicMock, call
import monitor

from cerberus.validator import DocumentError

############## CONFIG VALIDATION ##############

@pytest.mark.dependency()
def test_empty_config():
    '''
        Config validation with an empty config.yaml file
    '''

    config_path = "test_configs/empty.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)
    
    schema_path = "../config/schema.json"
    with open(os.path.join(os.path.dirname(__file__), schema_path)) as schema_file:
        schema = json.load(schema_file)

    with pytest.raises(DocumentError):
        monitor.validate_config(config, schema)

@pytest.mark.dependency()
def test_one_collector_config():
    '''
        Config validation with one valid collector
    '''

    config_path = "test_configs/one_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)
    
    schema_path = "../config/schema.json"
    with open(os.path.join(os.path.dirname(__file__), schema_path)) as schema_file:
        schema = json.load(schema_file)

    with pytest.raises(RuntimeError):
        monitor.validate_config(config, schema)

@pytest.mark.dependency()
def test_two_collector_config():
    '''
        Config validation with two valid collectors
    '''

    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)
    
    schema_path = "../config/schema.json"
    with open(os.path.join(os.path.dirname(__file__), schema_path)) as schema_file:
        schema = json.load(schema_file)

    assert monitor.validate_config(config, schema) == True

@pytest.mark.dependency()
def test_three_collector_config():
    '''
        Config validation with three valid collectors
    '''

    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)
    
    schema_path = "../config/schema.json"
    with open(os.path.join(os.path.dirname(__file__), schema_path)) as schema_file:
        schema = json.load(schema_file)

    assert monitor.validate_config(config, schema) == True

###############################################

#################### SETUP ####################

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_setup_two(mocker):
    '''
        Setup with two collectors
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_mock.return_value = mdt_instance
    

    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    monitor.setup(config)

    calls = [   
                call.create_destination('First-Collector', '4.5.6.7', 57777, 'self-describing-gpb', 'grpc', False, None),
                call.create_destination('Second-Collector', '7.6.5.4', 57777, 'self-describing-gpb', 'grpc', True, 'hostname.com'),
                call.create_sensor_path('Sample-Sensor-Group-Name', 'Cisco-IOS-XR-pfi-im-cmd-oper:interfaces/interface-xr/interface'),
                call.create_sensor_path('Sample-Sensor-Group-Name', 'Cisco-IOS-XR-infra-statsd-oper:infra-statistics/interfaces/interface/latest/data-rate')
            ]

    mdt_instance.assert_has_calls(calls, True)

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_setup_three(mocker):
    '''
        Setup with three collectors
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_mock.return_value = mdt_instance
    

    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    monitor.setup(config)

    calls = [   
                call.create_destination('First-Collector', '4.5.6.7', 57777, 'self-describing-gpb', 'grpc', False, None),
                call.create_destination('Second-Collector', '7.6.5.4', 57777, 'self-describing-gpb', 'grpc', True, 'hostname.com'),
                call.create_destination('Third-Collector', '1.2.3.4', 57777, 'self-describing-gpb', 'grpc', True, 'hostname2.com'),
                call.create_sensor_path('Sample-Sensor-Group-Name', 'Cisco-IOS-XR-pfi-im-cmd-oper:interfaces/interface-xr/interface'),
                call.create_sensor_path('Sample-Sensor-Group-Name', 'Cisco-IOS-XR-infra-statsd-oper:infra-statistics/interfaces/interface/latest/data-rate')
            ]

    mdt_instance.assert_has_calls(calls, True)

###############################################

#################### CLEAN ####################

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_clean_two_one_sub(mocker):
    '''
        Clean two collectors where second subscription is not configured
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", None])
    mdt_mock.return_value = mdt_instance
    

    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    monitor.clean(config)

    calls = [   
                call.delete_sensor_group('Sample-Sensor-Group-Name'),
                call.delete_sensor_group('Sample-Sensor-Group-Name-2'),
                call.delete_subscription('Subscription-1'),
                call.delete_destination_group('First-Collector'),
                call.delete_destination_group('Second-Collector')
            ]

    mdt_instance.assert_has_calls(calls, True)
    assert call.delete_subscription('Subscription-2') not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_clean_two_two_sub(mocker):
    '''
        Clean two collectors where both subscriptions are configured
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", "Another gNMI Response"])
    mdt_mock.return_value = mdt_instance
    

    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    monitor.clean(config)

    calls = [   
                call.delete_sensor_group('Sample-Sensor-Group-Name'),
                call.delete_sensor_group('Sample-Sensor-Group-Name-2'),
                call.delete_subscription('Subscription-1'),
                call.delete_destination_group('First-Collector'),
                call.delete_subscription('Subscription-2'),
                call.delete_destination_group('Second-Collector')
            ]

    mdt_instance.assert_has_calls(calls, True)

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_clean_three_one_sub(mocker):
    '''
        Clean three collectors where only the first subscription is configured
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", None, None])
    mdt_mock.return_value = mdt_instance
    

    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    monitor.clean(config)

    calls = [   
                call.delete_sensor_group('Sample-Sensor-Group-Name'),
                call.delete_sensor_group('Sample-Sensor-Group-Name-2'),
                call.delete_subscription('Subscription-1'),
                call.delete_destination_group('First-Collector'),
                call.delete_destination_group('Second-Collector'),
                call.delete_destination_group('Third-Collector')
            ]

    mdt_instance.assert_has_calls(calls, True)
    assert call.delete_subscription('Subscription-2') not in mdt_instance.mock_calls
    assert call.delete_subscription('Subscription-3') not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_clean_three_two_sub(mocker):
    '''
        Clean three collectors where only the first two subscriptions are configured
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", "Another gNMI Response", None])
    mdt_mock.return_value = mdt_instance
    

    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    monitor.clean(config)

    calls = [   
                call.delete_sensor_group('Sample-Sensor-Group-Name'),
                call.delete_sensor_group('Sample-Sensor-Group-Name-2'),
                call.delete_subscription('Subscription-1'),
                call.delete_destination_group('First-Collector'),
                call.delete_subscription('Subscription-2'),
                call.delete_destination_group('Second-Collector'),
                call.delete_destination_group('Third-Collector')
            ]

    mdt_instance.assert_has_calls(calls, True)
    assert call.delete_subscription('Subscription-3') not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_clean_three_three_sub(mocker):
    '''
        Clean three collectors where all three subscriptions are configured
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", "Another gNMI Response", "A third gNMI Response"])
    mdt_mock.return_value = mdt_instance
    

    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    monitor.clean(config)

    calls = [   
                call.delete_sensor_group('Sample-Sensor-Group-Name'),
                call.delete_sensor_group('Sample-Sensor-Group-Name-2'),
                call.delete_subscription('Subscription-1'),
                call.delete_destination_group('First-Collector'),
                call.delete_subscription('Subscription-2'),
                call.delete_destination_group('Second-Collector'),
                call.delete_subscription('Subscription-3'),
                call.delete_destination_group('Third-Collector')
            ]

    mdt_instance.assert_has_calls(calls, True)

###############################################

#################### CHECK ####################

# Different possible situations for a two collector system (9 important ones)
# Format: test_check_<NUMBER OF COLLECTORS>_<SITUATION #>
#
# 1. Create Subscription-1 and return with 0
# Subscription-1 : Doesn't Exist | ACTIVE
# Subscription-2 : Doesn't Exist | ACTIVE/INACTIVE
# ---------------------------------------
# 2. Return with 0
# Subscription-1 : Exists | ACTIVE
# Subscription-2 : Doesn't Exist | ACTIVE/INACTIVE
# ---------------------------------------
# 3. Delete Subscription-2 and return with 0
# Subscription-1 : Exists | ACTIVE
# Subscription-2 : Exists | ACTIVE/INACTIVE
# ---------------------------------------
# 4. Create Subscription-1 and Subscription-2 and return with 1
# Subscription-1 : Doesn't Exist | INACTIVE
# Subscription-2 : Doesn't Exist | ACTIVE
# ---------------------------------------
# 5. Create Subscription-2 and return with 1
# Subscription-1 : Exists | INACTIVE
# Subscription-2 : Doesn't Exist | ACTIVE
# ---------------------------------------
# 6. Return with 1
# Subscription-1 : Exists | INACTIVE
# Subscription-2 : Exists | ACTIVE
# ---------------------------------------
# 7. Create Subscription-1 and Subscription-2 and return with -1
# Subscription-1 : Doesn't Exist | INACTIVE
# Subscription-2 : Doesn't Exist | INACTIVE
# ---------------------------------------
# 8. Create Subscritpion-2 and return with -1
# Subscription-1 : Exists | INACTIVE
# Subscription-2 : Doesn't Exist | INACTIVE
# ---------------------------------------
# 9. Return with -1
# Subscription-1 : Exists | INACTIVE
# Subscription-2 : Exists | INACTIVE
# ---------------------------------------

# Different possible situations for a three collector system (16 important ones) 
# Format: test_check_<NUMBER OF COLLECTORS>_<SITUATION #>
# 
# ---------------------------------------
# 10. Return with -1
# Subscription-1: Exists | INACTIVE
# Subscription-2: Exists | INACTIVE
# Subscription-3: Exists | INACTIVE
# ---------------------------------------
# 11. Create Subscription-3 and return -1
# Subscription-1: Exists | INACTIVE
# Subscription-2: Exists | INACTIVE
# Subscription-3: Doesn't Exist | INACTIVE
# ---------------------------------------
# 12. Create Subscription-2 and Subscription-3 and return -1
# Subscription-1: Exists | INACTIVE
# Subscription-2: Doesn't Exist | INACTIVE
# Subscription-3: Doesn't Exist | INACTIVE
# ---------------------------------------
# 13. Create Subscription-1, Subscription-2, and Subscription-3 and return -1
# Subscription-1: Doesn't Exist | INACTIVE
# Subscription-2: Doesn't Exist | INACTIVE
# Subscription-3: Doesn't Exist | INACTIVE
# ---------------------------------------
# 14. Return 2
# Subscription-1: Exists | INACTIVE
# Subscription-2: Exists | INACTIVE
# Subscription-3: Exists | ACTIVE
# ---------------------------------------
# 15. Create Subscription-3 and return 2
# Subscription-1: Exists | INACTIVE
# Subscription-2: Exists | INACTIVE
# Subscription-3: Doesn't Exist | ACTIVE
# ---------------------------------------
# 16. Create Subscription-2 and Subscription-3 and return 2
# Subscription-1: Exists | INACTIVE
# Subscription-2: Doesn't Exist | INACTIVE
# Subscription-3: Doesn't Exist | ACTIVE
# ---------------------------------------
# 17. Create Subscription-1, Subscription-2, and Subscription-3 and return 2
# Subscription-1: Doesn't Exist | INACTIVE
# Subscription-2: Doesn't Exist | INACTIVE
# Subscription-3: Doesn't Exist | ACTIVE
# ---------------------------------------
# 18. Delete Subscription-3 and return 1
# Subscription-1: Exists | INACTIVE
# Subscription-2: Exists | ACTIVE
# Subscription-3: Exists | ACTIVE/INACTIVE
# ---------------------------------------
# 19. Return 1
# Subscription-1: Exists | INACTIVE
# Subscription-2: Exists | ACTIVE
# Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
# ---------------------------------------
# 20. Create Subscription-2 and return 1
# Subscription-1: Exists | INACTIVE
# Subscription-2: Doesn't Exist | ACTIVE
# Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
# ---------------------------------------
# 21. Create Subscription-1 and Subscription-2 and return 1
# Subscription-1: Doesn't Exist | INACTIVE
# Subscription-2: Doesn't Exist | ACTIVE
# Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
# ---------------------------------------
# 22. Delete Subscription-2 and Subscription-3 and return 0
# Subscription-1: Exists | ACTIVE
# Subscription-2: Exists | ACTIVE/INACTIVE
# Subscription-3: Exists | ACTIVE/INACTIVE
# ---------------------------------------
# 23. Delete Subscription-2 and return 0
# Subscription-1: Exists | ACTIVE
# Subscription-2: Exists | ACTIVE/INACTIVE
# Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
# ---------------------------------------
# 24. Return 0
# Subscription-1: Exists | ACTIVE
# Subscription-2: Doesn't Exist | ACTIVE/INACTIVE
# Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
# ---------------------------------------
# 25. Create Subscription-1 and return 0
# Subscription-1: Doesn't Exist | ACTIVE
# Subscription-2: Doesn't Exist | ACTIVE/INACTIVE
# Subscription-3: Doesn't Exist | ACTIVE/INACTIVE

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_check_two_1(mocker):
    '''
        1. Create Subscription-1 and return with 0
        Subscription-1 : Doesn't Exist | ACTIVE
        Subscription-2 : Doesn't Exist | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=[None, None])
    mdt_instance.check_connection = Mock(side_effect=[True, '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 0

    calls = [   
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000),
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_check_two_2(mocker):
    '''
        2. Return with 0
        Subscription-1 : Exists | ACTIVE
        Subscription-2 : Doesn't Exist | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", None])
    mdt_instance.check_connection = Mock(side_effect=[True, '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 0

    mdt_instance.create_subscription.assert_not_called()
    mdt_instance.delete_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_check_two_3(mocker):
    '''
        3. Delete Subscription-2 and return with 0
        Subscription-1 : Exists | ACTIVE
        Subscription-2 : Exists | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", "Another gNMI Response"])
    mdt_instance.check_connection = Mock(side_effect=[True, '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 0

    calls = [   
            call.delete_subscription('Subscription-2')
        ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.create_subscription.assert_not_called()
    assert call.delete_subscription('Subscription-1') not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_check_two_4(mocker):
    '''
        4. Create Subscription-1 and Subscription-2 and return with 1
        Subscription-1 : Doesn't Exist | INACTIVE
        Subscription-2 : Doesn't Exist | ACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=[None, None])
    mdt_instance.check_connection = Mock(side_effect=[False, True])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 1

    calls = [   
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000),
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_check_two_5(mocker):
    '''
        5. Create Subscription-2 and return with 1
        Subscription-1 : Exists | INACTIVE
        Subscription-2 : Doesn't Exist | ACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", None])
    mdt_instance.check_connection = Mock(side_effect=[False, True])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 1

    calls = [   
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000) not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_check_two_6(mocker):
    '''
        6. Return with 1
        Subscription-1 : Exists | INACTIVE
        Subscription-2 : Exists | ACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", "Another gNMI Response"])
    mdt_instance.check_connection = Mock(side_effect=[False, True])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 1

    mdt_instance.delete_subscription.assert_not_called()
    mdt_instance.create_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_check_two_7(mocker):
    '''
        7. Create Subscription-1 and Subscription-2 and return with -1
        Subscription-1 : Doesn't Exist | INACTIVE
        Subscription-2 : Doesn't Exist | INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=[None, None])
    mdt_instance.check_connection = Mock(side_effect=[False, False])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == -1

    calls = [   
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000),
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_check_two_8(mocker):
    '''
        8. Create Subscritpion-2 and return with -1
        Subscription-1 : Exists | INACTIVE
        Subscription-2 : Doesn't Exist | INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", None])
    mdt_instance.check_connection = Mock(side_effect=[False, False])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == -1

    calls = [   
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000) not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_two_collector_config"])
def test_check_two_9(mocker):
    '''
        9. return with -1
        Subscription-1 : Exists | INACTIVE
        Subscription-2 : Exists | INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", "Another gNMI Response"])
    mdt_instance.check_connection = Mock(side_effect=[False, False])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/two_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == -1

    mdt_instance.create_subscription.assert_not_called()
    mdt_instance.delete_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_10(mocker):
    '''
        10. Return with -1
        Subscription-1: Exists | INACTIVE
        Subscription-2: Exists | INACTIVE
        Subscription-3: Exists | INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", "Another gNMI Response", "A third gNMI Response"])
    mdt_instance.check_connection = Mock(side_effect=[False, False, False])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == -1

    mdt_instance.create_subscription.assert_not_called()
    mdt_instance.delete_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_11(mocker):
    '''
        11. Create Subscription-3 and return -1
        Subscription-1: Exists | INACTIVE
        Subscription-2: Exists | INACTIVE
        Subscription-3: Doesn't Exist | INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", "Another gNMI Response", None])
    mdt_instance.check_connection = Mock(side_effect=[False, False, False])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == -1

    calls = [   
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name', 'Third-Collector', 30000),
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name-2', 'Third-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000) not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_12(mocker):
    '''
        12. Create Subscription-2 and Subscription-3 and return -1
        Subscription-1: Exists | INACTIVE
        Subscription-2: Doesn't Exist | INACTIVE
        Subscription-3: Doesn't Exist | INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["Some gNMI Response", None, None])
    mdt_instance.check_connection = Mock(side_effect=[False, False, False])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == -1

    calls = [   
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name', 'Third-Collector', 30000),
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name-2', 'Third-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000) not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_13(mocker):
    '''
        13. Create Subscription-1, Subscription-2, and Subscription-3 and return -1
        Subscription-1: Doesn't Exist | INACTIVE
        Subscription-2: Doesn't Exist | INACTIVE
        Subscription-3: Doesn't Exist | INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=[None, None, None])
    mdt_instance.check_connection = Mock(side_effect=[False, False, False])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == -1

    calls = [   
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name', 'Third-Collector', 30000),
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name-2', 'Third-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000),
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000),
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_14(mocker):
    '''
        14. Return 2
        Subscription-1: Exists | INACTIVE
        Subscription-2: Exists | INACTIVE
        Subscription-3: Exists | ACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["A gNMI Response", "Another gNMI Response", "A third gNMI Response"])
    mdt_instance.check_connection = Mock(side_effect=[False, False, True])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 2

    mdt_instance.delete_subscription.assert_not_called()
    mdt_instance.create_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_15(mocker):
    '''
        15. Create Subscription-3 and return 2
        Subscription-1: Exists | INACTIVE
        Subscription-2: Exists | INACTIVE
        Subscription-3: Doesn't Exist | ACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["A gNMI Response", "Another gNMI Response", None])
    mdt_instance.check_connection = Mock(side_effect=[False, False, True])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 2

    calls = [   
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name', 'Third-Collector', 30000),
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name-2', 'Third-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()
    assert call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000) not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_16(mocker):
    '''
        16. Create Subscription-2 and Subscription-3 and return 2
        Subscription-1: Exists | INACTIVE
        Subscription-2: Doesn't Exist | INACTIVE
        Subscription-3: Doesn't Exist | ACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["A gNMI Response", None, None])
    mdt_instance.check_connection = Mock(side_effect=[False, False, True])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 2

    calls = [   
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name', 'Third-Collector', 30000),
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name-2', 'Third-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000) not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_17(mocker):
    '''
        17. Create Subscription-1, Subscription-2, and Subscription-3 and return 2
        Subscription-1: Doesn't Exist | INACTIVE
        Subscription-2: Doesn't Exist | INACTIVE
        Subscription-3: Doesn't Exist | ACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=[None, None, None])
    mdt_instance.check_connection = Mock(side_effect=[False, False, True])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 2

    calls = [   
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name', 'Third-Collector', 30000),
                call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name-2', 'Third-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000),
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000),
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_18(mocker):
    '''
        18. Delete Subscription-3 and return 1
        Subscription-1: Exists | INACTIVE
        Subscription-2: Exists | ACTIVE
        Subscription-3: Exists | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["A gNMI Response", "Another gNMI Response", "A third gNMI Response"])
    mdt_instance.check_connection = Mock(side_effect=[False, True, '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 1

    calls = [
                call.delete_subscription('Subscription-3')
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.create_subscription.assert_not_called()
    assert call.delete_subscription('Subscription-1') not in mdt_instance.mock_calls
    assert call.delete_subscription('Subscription-2') not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_19(mocker):
    '''
        19. Return 1
        Subscription-1: Exists | INACTIVE
        Subscription-2: Exists | ACTIVE
        Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["A gNMI Response", "Another gNMI Response", None])
    mdt_instance.check_connection = Mock(side_effect=[False, True, '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 1

    mdt_instance.delete_subscription.assert_not_called()
    mdt_instance.create_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_20(mocker):
    '''
        20. Create Subscription-2 and return 1
        Subscription-1: Exists | INACTIVE
        Subscription-2: Doesn't Exist | ACTIVE
        Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["A gNMI Response", None, None])
    mdt_instance.check_connection = Mock(side_effect=[False, True, '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 1

    calls = [   
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name', 'Third-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name-2', 'Third-Collector', 30000) not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_21(mocker):
    '''
        21. Create Subscription-1 and Subscription-2 and return 1
        Subscription-1: Doesn't Exist | INACTIVE
        Subscription-2: Doesn't Exist | ACTIVE
        Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=[None, None, None])
    mdt_instance.check_connection = Mock(side_effect=[False, True, '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 1

    calls = [   
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000),
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000),
                call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()
    assert call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name', 'Third-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name-2', 'Third-Collector', 30000) not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_22(mocker):
    '''
        22. Delete Subscription-2 and Subscription-3 and return 0
        Subscription-1: Exists | ACTIVE
        Subscription-2: Exists | ACTIVE/INACTIVE
        Subscription-3: Exists | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["A gNMI Response", "Another gNMI Response", "A third gNMI Response"])
    mdt_instance.check_connection = Mock(side_effect=[True, '?', '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 0

    calls = [
                call.delete_subscription('Subscription-2'),
                call.delete_subscription('Subscription-3')
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.create_subscription.assert_not_called()
    assert call.delete_subscription('Subscription-1') not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_23(mocker):
    '''
        23. Delete Subscription-2 and return 0
        Subscription-1: Exists | ACTIVE
        Subscription-2: Exists | ACTIVE/INACTIVE
        Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["A gNMI Response", "Another gNMI Response", None])
    mdt_instance.check_connection = Mock(side_effect=[True, '?', '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 0

    calls = [
                call.delete_subscription('Subscription-2')
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.create_subscription.assert_not_called()
    assert call.delete_subscription('Subscription-1') not in mdt_instance.mock_calls
    assert call.delete_subscription('Subscription-3') not in mdt_instance.mock_calls

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_24(mocker):
    '''
        24. Return 0
        Subscription-1: Exists | ACTIVE
        Subscription-2: Doesn't Exist | ACTIVE/INACTIVE
        Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=["A gNMI Response", None, None])
    mdt_instance.check_connection = Mock(side_effect=[True, '?', '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 0

    mdt_instance.create_subscription.assert_not_called()
    mdt_instance.delete_subscription.assert_not_called()

@pytest.mark.dependency(depends=["test_three_collector_config"])
def test_check_three_25(mocker):
    '''
        25. Create Subscription-1 and return 0
        Subscription-1: Doesn't Exist | ACTIVE
        Subscription-2: Doesn't Exist | ACTIVE/INACTIVE
        Subscription-3: Doesn't Exist | ACTIVE/INACTIVE
    '''

    mdt_mock = mocker.patch('monitor.MDT')

    mdt_instance = MagicMock()
    mdt_instance.__enter__.return_value = mdt_instance
    mdt_instance.__exit__.return_value = None
    mdt_instance.read_subscription = Mock(side_effect=[None, None, None])
    mdt_instance.check_connection = Mock(side_effect=[True, '?', '?'])
    mdt_mock.return_value = mdt_instance
    
    config_path = "test_configs/three_collector.yaml"
    with open(os.path.join(os.path.dirname(__file__), config_path), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.Loader)

    assert monitor.check(config) == 0

    calls = [
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name', 'First-Collector', 30000),
                call.create_subscription('Subscription-1', 'Sample-Sensor-Group-Name-2', 'First-Collector', 30000)
            ]

    mdt_instance.assert_has_calls(calls, True)
    mdt_instance.delete_subscription.assert_not_called()
    assert call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name', 'Second-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-2', 'Sample-Sensor-Group-Name-2', 'Second-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name', 'Third-Collector', 30000) not in mdt_instance.mock_calls
    assert call.create_subscription('Subscription-3', 'Sample-Sensor-Group-Name-2', 'Third-Collector', 30000) not in mdt_instance.mock_calls

###############################################