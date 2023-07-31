FROM tensorflow/tensorflow:latest

COPY requirements.txt /tmp/swarmlib/

COPY train.npz /tmp
COPY test.npz /tmp

# Install ml environment packages
RUN pip3 install --upgrade pip && pip3 install -r /tmp/swarmlib/requirements.txt

# Install SwarmLearning package, make sure package version matches with Swarm release you are using.
RUN pip3 install https://github.com/HewlettPackard/swarm-learning/raw/master/lib/swarmlearning-client-py3-none-manylinux_2_24_x86_64.whl
