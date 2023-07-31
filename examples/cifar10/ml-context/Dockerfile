######################################################################
# (C)Copyright 2021,2022 Hewlett Packard Enterprise Development LP
######################################################################
# This is a sample docker file to build the user ml container

FROM tensorflow/tensorflow:2.7.0

COPY requirements.txt /tmp/swarmlib/

# Install ml environment packages
RUN pip3 install --upgrade pip && pip3 install -r /tmp/swarmlib/requirements.txt

# Install SwarmLearning package, make sure package version matches with Swarm release you are using
RUN pip3 install  https://github.com/HewlettPackard/swarm-learning/raw/master/lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl
