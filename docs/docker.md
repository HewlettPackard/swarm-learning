
## Docker Installation
If you do not already have Docker installed, follow the instructions to install docker for below Linux platforms.
- [Linux](https://docs.docker.com/engine/install/ubuntu/)
- [RHEL](https://docs.docker.com/engine/install/rhel/)

## Docker Commands

Below are some helpful docker commands to work with Swarm Learning.<br> 
To learn more on Docker CLI, [Click here](https://docs.docker.com/reference/).

### - docker login
This command helps you to log into your docker hub.<br>
e.g. docker login -u <user-name> <docker-hub><br>
Refer https://docs.docker.com/engine/reference/commandline/login/<br>
  
### - docker pull
This command pulls a specific image from the Docker Hub. All you have to do is use the command ‘docker pull’ along with the name of the image.<br>
e.g. docker pull hub.myenterpriselicense.hpe.com/hpe_eval/swarm-learning/sn:1.2.0 <br>
Refer https://docs.docker.com/engine/reference/commandline/pull/

### - docker images
This command shows all top-level images, their repository and tags, and their size.<br>
Refer https://docs.docker.com/engine/reference/commandline/images/

### - docker rmi
This command is used to free up some disk space. The image id is used to remove the image while using this command.<br>
e.g. docker rmi <image-name> <br>
Refer https://docs.docker.com/engine/reference/commandline/rmi/

### - docker ps -a
This command is used to know the details of all the running, stopped, or exited containers.<br>
Refer https://docs.docker.com/engine/reference/commandline/ps/

### - docker rm
This command is used to remove (kill) one or more containers.<br>
e.g. docker rm -f <container-name-1> <container-name-2> … <br>
Refer https://docs.docker.com/engine/reference/commandline/rm/

### - docker logs
This command is used to check the logs of all the docker containers with the corresponding contained id mentioned in the command.<br>
e.g <br>
docker logs <container-name> - Logs only till current execution of the container.<br>
docker logs -f <container-name> - Continues to log till container is executing.<br>
Refer https://docs.docker.com/engine/reference/commandline/logs/

### - docker exec
This command is used to access the container that is running and enables to run a new command in the container.<br>
e.g. docker exec -it <container-name> bash – This runs bash session inside the container.<br>
Refer https://docs.docker.com/engine/reference/commandline/exec/

### - docker run
This command is used to create a container from an image.<br>
Refer https://docs.docker.com/engine/reference/commandline/run/

### - docker volume
This command creates a volume so that the docker container can use it to store data.<br>
Refer https://docs.docker.com/engine/reference/commandline/volume_create/

### - docker stop 
The ‘docker stop’ command stops a container using the container name or its id.<br>
Refer https://docs.docker.com/engine/reference/commandline/stop/

### - docker restart
This command is used to restart the stopped container. It is recommended to use this after rebooting the system.<br>
Refer https://docs.docker.com/engine/reference/commandline/restart/

### - docker kill
This command is used to stop the container immediately by killing its execution.<br>
Refer https://docs.docker.com/engine/reference/commandline/kill/

### - docker network 
The ‘docker network’ command is used to know the details of the list of networks in the cluster.<br>
Refer https://docs.docker.com/engine/reference/commandline/network/
