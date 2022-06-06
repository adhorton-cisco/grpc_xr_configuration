from config_telemetry import TelemetryConfig
from grpc.framework.interfaces.face.face import ExpirationError

def user_input(_type, message):
    invalidInput = True
    response = None
    while invalidInput:
        try:
            response = input(message)
            if _type == "int":
                response = int(response)
            invalidInput = False
        except ValueError:
            print("Invalid Input. Try Again.\n")
    return response

##To-do: Automatically load in current configuration into stored destination groups/sensor groups/subscriptions
def user_friendly_menu():
    choice = -1
    dest_groups = {}
    sensor_groups = {}
    subscriptions = {}

    menu = (
        "\n0: Print Menu\n"
        "1: Push Sample Configuration\n"
        "2: Create Destination Group\n"
        "3: Create a Sensor Group\n"
        "4: Create a Subscription\n"
        "5: Push a Configuration\n"
        "6: Get Running Configuration\n"
        "7: Clear a Configuration\n"
        "8: Clear ALL Configurations\n"
        "9: Exit\n"
    )

    routerIP = user_input("str", "Router IP Address: ")
    port = user_input("int", "Router Port: ")
    timeout = user_input("int", "Timeout: ")
    user = user_input("str", "Username: ")
    password = user_input("str", "Password: ")

    config = TelemetryConfig(routerIP, port, timeout, user, password)
    try:
        config.get_config()
        print(menu)
    except ExpirationError:
        choice = 9
        print("Failed to connect to Router!")

    while choice != 9:
        choice = user_input("int", "Select an Option (0-9): ")

        ## Print Menu ##
        if choice == 0:
            print(menu)
        
        ## Push Sample Configuration ##
        elif choice == 1:
            dg = TelemetryConfig.Destination_Group('DGroup1')
            dg.add_destination('1.1.1.1', 57500, 'self-describing-gpb', 'grpc')
            dg.add_destination('2.2.2.2', 57500, 'self-describing-gpb', 'grpc')
            print("Created Destination Group: DGroup1")
            config.create_destination_group(dg)
            print("Pushed DGroup1 to Router")

            sg = TelemetryConfig.Sensor_Group('SGroup1')
            sg.add_sensor_path('Cisco-IOS-XR-nto-misc-oper:memory-summary/nodes/node/summary')
            sg.add_sensor_path('Cisco-IOS-XR-nto-misc-oper:memory-summary/nodes/node/detail')
            print("Created Sensor Group: SGroup1")
            config.create_sensor_group(sg)
            print("Pushed SGroup1 to Router")

            sub = TelemetryConfig.Subscription('Sub1', dg, sg, 30000)
            print("Created Subscription: Sub1")
            config.create_subscription(sub)
            print("Pushed Sub1 to Router\n")

        ## Create Destination Group ##
        elif choice == 2:
            destName = user_input("str", "Name of Destination Group: ")
            dg = TelemetryConfig.Destination_Group(destName)
            destChoice = -1
            destMenu = "\n0: Print Mini Menu\n1: Add Destination\n2: Exit to Main Menu\n"
            print(destMenu)
            while destChoice != 2:
                destChoice = user_input("int", "Select an Option (0-2): ")
                if destChoice == 0:
                    print(destMenu)
                elif destChoice == 1:
                    destIP = user_input("str", "Enter Destination IP: ")
                    destPort = user_input("int", "Enter Destination Port: ")
                    destEncoding = user_input("str", "Enter Encoding: ")
                    destProtocol = user_input("str", "Enter Protocol: ")
                    print()
                    dg.add_destination(destIP, destPort, destEncoding, destProtocol)
                elif destChoice == 2:
                    print("Destination Group Created\n")
                    dest_groups[dg.name] = dg
                else:
                    print("Invalid Input. Try Again.\n")

        ## Create Sensor Group ##
        elif choice == 3:
            sensName = user_input("str", "Name of Sensor Group: ")
            sg = TelemetryConfig.Sensor_Group(sensName)
            sensChoice = -1
            sensMenu = "\n0: Print Mini Menu\n1: Add Sensor Path\n2: Exit to Main Menu\n"
            print(sensMenu)
            while sensChoice != 2:
                sensChoice = user_input("int", "Select an Option (0-2): ")
                if sensChoice == 0:
                    print(sensMenu)
                elif sensChoice == 1:
                    sensorPath = user_input("str", "Enter Sensor Path: ")
                    print()
                    sg.add_sensor_path(sensorPath)
                elif sensChoice == 2:
                    print("Sensor Group Created\n")
                    sensor_groups[sg.name] = sg
                else:
                    print("Invalid Input. Try Again.\n")

        ## Create Subscription ##
        elif choice == 4:
            if len(dest_groups) == 0 or len(sensor_groups) == 0:
                print("Must Create a Destination Group and Sensor Group Before a Subscription")
                continue
            subName = user_input("str", "Name of Subscription: ")
            subInterval = user_input("int", "Streaming Interval: ")

            print("\n---Destination Groups---")
            for dest_group in dest_groups.keys():
                print(dest_group)
            print()
            dgName = user_input("str", "Destination Group: ")
            while dgName not in dest_groups.keys():
                print(dgName + " is not a valid Destination Group. Try Again.\n")
                dgName = user_input("str", "Destination Group: ")

            print("\n---Sensor Groups---")
            for sens_group in sensor_groups.keys():
                print(sens_group)
            print()
            sgName = user_input("str", "Sensor Group: ")
            while sgName not in sensor_groups.keys():
                print(sgName + " is not a valid Sensor Group. Try Again.\n")
                sgName = user_input("str", "Sensor Group: ")
            
            newSubscription = TelemetryConfig.Subscription(subName, sensor_groups[sgName], dest_groups[dgName], subInterval)
            subscriptions[newSubscription.name] = newSubscription
            print("Subscription Created\n")

        ## Push Configuration ##
        elif choice == 5:
            pushChoice = -1
            pushMenu = "\n0: Print Mini Menu\n1: Push a Destination Group\n2: Push a Sensor Group\n3: Push a Subscription\n4: Exit to Main Menu\n"
            print(pushMenu)
            while pushChoice != 4:
                pushChoice = user_input("int", "Choose an Option (0-4): ")
                if pushChoice == 0:
                    print(pushMenu)
                elif pushChoice == 1:
                    if len(dest_groups) == 0:
                        print("No Destination Groups\n")
                        continue
                    print("\n---Destination Groups---")
                    for dest_group in dest_groups.keys():
                        print(dest_group)
                    print()
                    dgName = user_input("str", "Destination Group: ")
                    while dgName not in dest_groups.keys():
                        print(dgName + " is not a valid Destination Group. Try Again.\n")
                        dgName = user_input("str", "Destination Group: ")
                    config.create_destination_group(dest_groups[dgName])
                    print("Destination Group \"" + dgName + "\" is Pushed\n")
                elif pushChoice == 2:
                    if len(sensor_groups) == 0:
                        print("No Sensor Groups\n")
                        continue
                    print("\n---Sensor Groups---")
                    for sensor_group in sensor_groups.keys():
                        print(sensor_group)
                    print()
                    sgName = user_input("str", "Sensor Group: ")
                    while sgName not in sensor_groups.keys():
                        print(sgName + " is not a valid Sensor Group. Try Again.\n")
                        sgName = user_input("str", "Sensor Group: ")
                    config.create_sensor_group(sensor_groups[sgName])
                    print("Sensor Group \"" + sgName + "\" is Pushed\n")
                elif pushChoice == 3:
                    if len(subscriptions) == 0:
                        print("No Subscriptions\n")
                        continue
                    print("\n---Subscriptions---")
                    for subscription in subscriptions.keys():
                        print(subscription)
                    print()
                    subName = user_input("str", "Subscription: ")
                    while subName not in subscriptions.keys():
                        print(subName + " is not a valid Subscription. Try Again.\n")
                        subName = user_input("str", "Subscription: ")
                    config.create_subscription(subscriptions[subName])
                    print("Subscription \"" + subName + "\" is Pushed\n")
                elif pushChoice == 4:
                    print("Returning to Main Menu\n")
                else:
                    print("Invalid Input. Try Again.\n")
        
        ## Get Running Configuration ##
        elif choice == 6:
            print(config.get_config())

        ## Clear a Configuration ##
        elif choice == 7:
            clearChoice = -1
            clearMenu = "\n0: Print Mini Menu\n1: Clear a Destination Group\n2: Clear a Sensor Group\n3: Clear a Subscription\n4: Exit to Main Menu"
            print(clearMenu)
            while clearChoice != 4:
                clearChoice = user_input("int", "Choose an Option (0-4): ")
                if clearChoice == 0:
                    print(clearMenu)
                elif clearChoice == 1:
                    if len(dest_groups) == 0:
                        print("No Destination Groups\n")
                        continue
                    print("\n---Destination Groups---")
                    for dest_group in dest_groups.keys():
                        print(dest_group)
                    print()
                    dgName = user_input("str", "Destination Group: ")
                    while dgName not in dest_groups.keys():
                        print(dgName + " is not a valid Destination Group. Try Again.\n")
                        dgName = user_input("str", "Destination Group: ")
                    config.delete_config(target=dest_groups[dgName])
                    print("Destination Group \"" + dgName + "\" is Cleared\n")
                elif clearChoice == 2:
                    if len(sensor_groups) == 0:
                        print("No Sensor Groups\n")
                        continue
                    print("\n---Sensor Groups---")
                    for sensor_group in sensor_groups.keys():
                        print(sensor_group)
                    print()
                    sgName = user_input("str", "Sensor Group: ")
                    while sgName not in sensor_groups.keys():
                        print(sgName + " is not a valid Sensor Group. Try Again.\n")
                        sgName = user_input("str", "Sensor Group: ")
                    config.delete_config(target=sensor_groups[sgName])
                    print("Sensor Group \"" + sgName + "\" is Cleared\n")
                elif clearChoice == 3:
                    if len(subscriptions) == 0:
                        print("No Subscriptions\n")
                        continue
                    print("\n---Subscriptions---")
                    for subscription in subscriptions.keys():
                        print(subscription)
                    print()
                    subName = user_input("str", "Subscription: ")
                    while subName not in subscriptions.keys():
                        print(subName + " is not a valid Subscription. Try Again.\n")
                        subName = user_input("str", "Subscription: ")
                    config.delete_config(target=subscriptions[subName])
                    print("Subscription \"" + subName + "\" is Cleared\n")
                elif clearChoice == 4:
                    print("Returning to Main Menu\n")
                else:
                    print("Invalid Input. Try Again.\n")

        ## Clear ALL Configurations ##
        elif choice == 8:
            confirmation = user_input("str", "Are You Sure You Want to Clear ALL Configurations? [y/n]: ")
            if confirmation == "y":
                config.delete_config()
                print("All Configurations Cleared\n")
            else:
                print("No Changes Made")

        ## Exit ##
        elif choice == 9:
            print("Goodbye!")  
        else:
            print("Invalid Input. Try Again.\n")


if __name__ == '__main__':
    user_friendly_menu()
