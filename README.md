# DockerStats
This is the repository for a Docker container that periodically posts statistics about its host to a provided endpoint. Only CPU and memory usage information is collected for the time being.

## The Docker Image
The image is built on top of a clean Alpine implementation, and is 33MB uncompressed. Other than standard Alpine Linux, it comes with python3, pip and the Python package ```requests``` installed.

## The Python Module
```main.py``` periodically reads data from the /proc directory and compiles a json object of CPU and memory usage statistics. This period is set to 5 seconds as the default, and can be configured. The statistics are then posted to an HTTP endpoint.

## Usage
To build the latest Docker image, run the command ```make build```. By default this builds the container specified in the Dockerfile with the name ```docker-stats```

To run a container with the image run the command ```make run```. By default, this runs the latest ds-stats image and mounts the /proc folder as /host-proc.

To build and run an image, you can just call ```make```