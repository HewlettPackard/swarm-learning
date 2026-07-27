FROM tensorflow/tensorflow:2.7.0

COPY requirements.txt swarmlearning-*.whl /tmp/swarmlib/

RUN pip3 install --upgrade pip && \
    pip3 install -r /tmp/swarmlib/requirements.txt

RUN pip3 install /tmp/swarmlib/swarmlearning-*.whl
