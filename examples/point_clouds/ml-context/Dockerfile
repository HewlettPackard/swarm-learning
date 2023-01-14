######################################################################
# (C)Copyright 2021,2022 Hewlett Packard Enterprise Development LP
######################################################################
# This is a sample docker file to build the user ml container

FROM pytorch/pytorch:1.5-cuda10.1-cudnn7-runtime

COPY requirements.txt swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl /tmp/swarmlib/

# Setup conda dev environment
RUN apt-get update && apt-get install \
    build-essential python3-dev python3-pip \
    python3-setuptools --no-install-recommends -y

RUN apt-get install libglib2.0-0 -y

# Install conda
RUN conda install pip

# Install ml environment packages
RUN pip3 install --upgrade pip && pip3 install -r /tmp/swarmlib/requirements.txt

# Install SwarmLearning package
RUN pip3 install /tmp/swarmlib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl
