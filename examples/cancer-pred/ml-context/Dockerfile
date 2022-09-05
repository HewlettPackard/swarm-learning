FROM tensorflow/tensorflow:latest

COPY requirements.txt swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl /tmp/swarmlib/

# Install ml environment packages
RUN pip3 install --upgrade pip && pip3 install -r /tmp/swarmlib/requirements.txt

# Install SwarmLearning package
RUN pip3 install /tmp/swarmlib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl
