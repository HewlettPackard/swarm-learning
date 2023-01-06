#!/bin/bash
######################################################################
## (C)Copyright 2023 Hewlett Packard Enterprise Development LP
######################################################################
######################################################################
# SWARM LEARNING SCRIPT TO TAKE LOGS.
# The tar archive includes
#   => Output of swarmLogCollector.sh script [OS info, nvidia-smi, docker ps -a] 
#	=>  Docker logs from all Swarm artifacts: [SN, SWOP, SWCI, SL, ML]
#########################################################################
set -x #Debug ON

#Checking docker hub passed as argument. If not, exiting
if [ -z "$1" ]
  then
    echo `date`"-ERROR: DOCKER HUB ARGUMENT IS EMPTY..Exiting!!"
    exit 1
fi

#docker hub or ml image path passed as argument. If not, exiting
if [ -z "$2" ]
  then
    echo `date`"-ERROR: You have to provide absolute path to workspace(if using SWOP to running examples or ML Image name (If using run SL script) !!"
    exit 1
fi

hostname=$(hostname)
dt=$(date +%Y%m%d%H%M%S)

LOG_DIR="swarm_logs_$hostname_$dt"

#Creating dir for saving logs 
mkdir -m 777 "$LOG_DIR"

#Checking user using SWOP or SL to run the command.
IFS='=' read -ra parse_ml_or_swop <<< $2

if [ "${parse_ml_or_swop[0]}" == "mlimage" ] ; then
  USER_CONTAINERS=${parse_ml_or_swop[1]}
elif [ "${parse_ml_or_swop[0]}" == "workspace" ] ; then
  WORKSPACE=${parse_ml_or_swop[1]}
  IFS=':' read -ra  user_container <<< $(cat $WORKSPACE/swci/taskdefs/user_env_tf_build_task.yaml | grep Outcome)
  USER_CONTAINERS_=${user_container[1]}
  USER_CONTAINERS="$(echo -e "${USER_CONTAINERS_}" | tr -d '[:space:]')"

  cp $WORKSPACE/swci/taskdefs/*.yaml "$LOG_DIR"/
  cp $WORKSPACE/swop/*.yaml "$LOG_DIR"/  
else
  echo `date`"-ERROR: Either mlimage or workspace should be passed..Exiting!!"
  exit 1
fi

# Checking the user image exists or not 
echo "User Container is: $USER_CONTAINERS"
if [[ "$(docker images -q $USER_CONTAINERS:latest 2> /dev/null)" == "" ]]; then
  echo `date`"-ERROR: $USER_CONTAINERS:latest not exists"
fi

#Capturing output of "id"
echo "id:"
id 
#Getting OS info
# This command will work in ubuntu and RHEL
# ######## Sample output from ubuntu  ############
# No LSB modules are available.
# Distributor ID: Ubuntu
# Description:    Ubuntu 20.04.3 LTS
# Release:        20.04
# Codename:       focal
# #########Sample output from RHEL ############
# LSB Version:    # :core-4.1-amd64:core-4.1-noarch:cxx-4.1-amd64:cxx-4.1-noarch:desktop-4.1-amd64:desktop-4.1-noarch:languages-4.1-amd64:languages-4.1-noarch:printing-4.1-amd64:printing-4.1-noarch
# Distributor ID: RedHatEnterprise
# Description:    Red Hat Enterprise Linux release 8.5 (Ootpa)
# Release:        8.5
# Codename:       Ootpa

echo "OS details:"
lsb_release -a

echo "Docker Version Details:"
docker version

echo "Docker Info:"
docker info

echo "Running and exited dockers details:"
docker ps -a

echo "NVIDIA DETAILS"
nvidia-smi

DOCKER_HUB=$1
TAG=$(docker images | grep $DOCKER_HUB/sn  | awk '{print $2}')

#Looping through images and checking all images exists. 
for image in swop swci sn sl
 do
    if [[ "$(docker images -q $DOCKER_HUB/$image:$TAG 2> /dev/null)" == "" ]]; then
        echo `date`"-ERROR: $DOCKER_HUB/$image:$TAG not exists"
	else
	    echo `date`"-INFO: $DOCKER_HUB/$image:$TAG exists.."		
    fi		
 done

########### BEGING TAKING SNs LOGS######################
SNs=$(docker ps -a -q  --filter ancestor=$DOCKER_HUB/sn:$TAG)
sns_array=($SNs)
for index in "${!sns_array[@]}"
  do
	docker logs ${sns_array[index]} > "$LOG_DIR"/sn_$index.log 
	docker inspect ${sns_array[index]} > "$LOG_DIR"/sn_inspect_$index.log
  done
########### END TAKING SNs LOGS######################

########### BEGIN TAKING SWOPs LOGS######################
SWOPs=$(docker ps -a -q  --filter ancestor=$DOCKER_HUB/swop:$TAG)
swops_array=($SWOPs)
for index in "${!swops_array[@]}"
  do
	docker logs ${swops_array[index]}  > "$LOG_DIR"/swop_$index.log
	docker inspect ${swops_array[index]} > "$LOG_DIR"/swop_inspect_$index.log
  done
########### END TAKING SWOPs LOGS######################

########### BEGIN TAKING SLs LOGS######################
SLs=$(docker ps -a -q  --filter ancestor=$DOCKER_HUB/sl:$TAG)
sls_array=($SLs)
for index in "${!sls_array[@]}"
do
	docker logs ${sls_array[index]}  > "$LOG_DIR"/sl_$index.log 
	docker inspect ${sls_array[index]} > "$LOG_DIR"/sl_inspect_$index.log
done
########### TAKING SNs LOGS######################

########### BEGIN TAKING USER LOGS######################
MLs=$(docker ps -a -q  --filter ancestor=$USER_CONTAINERS)
mls_array=($MLs)
for index in "${!mls_array[@]}"
do
    echo "INFO: capturing log for ${mls_array[index]}"
    docker logs ${mls_array[index]}  > "$LOG_DIR"/user_$index.log
	docker inspect ${mls_array[index]} > "$LOG_DIR"/ml_inspect_$index.log
done
########### END TAKING USER LOGS######################

echo "Python Libraries"
pip list

cp out.log  "$LOG_DIR"/out.log
tar -czvf "$LOG_DIR.tar.gz" "$LOG_DIR"
