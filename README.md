# Telemetry Collector Health Monitor for IOS-XR
This repository contains the source code for a docker image that can be built and run on IOS-XR to redirect the streaming of telemetry data to an active backup collector when a primary collector goes down for any reason. It will automatically reconfigure the router to send telemetry data back to the primary collector when it comes back up. It runs in the backround as a docker container managed by the IOS-XR appmgr.

Find the latest docker image at the [Docker Hub](https://hub.docker.com/r/adhorton/xr-collector-health-monitor)

If you discover any problems or need help, create an issue or contact me directly at adhorton@cisco.com

## Installation
1. Build Image from Scratch OR Pull from Docker Hub
    
    a) Build from Scratch
    - Clone Repository
    ```sh
    git clone https://github.com/adhorton-cisco/xr-collector-health-monitor.git
    ```
    - Build Image in Root Directory of Repository
    ```sh
    docker build -t <NAME-OF-YOUR-IMAGE> .
    ```    
    
    b) Pull from Docker Hub
    ```sh
    docker pull adhorton/xr-collector-health-monitor:<VERSION>
    ```

2. Save Image to .tar File
    ```sh
    docker save <IMAGE-NAME:TAG> > <NAME>.tar
    ```

3. Package Application as RPM
    - Follow Instructions from [xr-appmgr-build](https://github.com/ios-xr/xr-appmgr-build)

4. Transfer .rpm File to /misc/app_host Directory on Router
   ```sh
   scp /path/to/your/file/<NAME>.rpm user@router:/misc/app_host
   ```

5. Create config.yaml File
    - Create a file named "config.yaml" in an empty directory that follows the conventions layed out in config/sample.yaml. This will be mounted into the running application to tell it information about the different collectors on the network and the desired telemetry configuration. To enter the Linux environment from IOS-XR, use the "bash" command.

6. Install RPM Package to appmgr
    - In the IOS-XR CLI, 
    ```sh
    appmgr package install rpm /misc/app_host/<NAME>.rpm
    ```
    - To confirm that the package is installed
    ```
    show appmgr packages installed
    ```

7. Activate the Application
    - Enter the config menu
    - Activate the application
    ```sh
    appmgr application <NAME> activate type docker source <NAME> docker-run-opts "-itd -v /path/to/config/file:/config:ro --network host"
    ```
    - Commit configuration
    - Application will automatically configure streaming telemetry to the first active collector
    - Confirm that application is running successfully
    ```sh
    show appmgr application name <NAME> info summary
    ```

## Using IOS-XR appmgr
- View application logs
    ```sh
    show appmgr application name <NAME> logs
    ```

- Start/Stop applications
    ```sh
    appmgr application <start/stop> name <NAME>
    ```
    
- Show all applications (Similar to docker ps -a)
    ```sh
    show appmgr application-table
    ```

- Uninstall package
    ```sh
    appmgr package uninstall package <NAME>
    ```

## Useful Links

For additional resources on telemetry, app hosting, or anything else to do with IOS-XR, visit [xrdocs](https://xrdocs.io/)

## Contributors/Contact
* Adam Horton - adhorton@cisco.com

Project Link: [https://github.com/adhorton-cisco/xr-collector-health-monitor](https://github.com/adhorton-cisco/xr-collector-health-monitor)
