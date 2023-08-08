FROM ubuntu:22.04

RUN apt-get update && \
        apt-get install software-properties-common -y && \
        add-apt-repository ppa:deadsnakes/ppa -y && \
        apt-get update && \
        apt-get install -y --no-install-recommends python3.10 python3-pip python3-dev libssl-dev

COPY ["requirements.txt", "/tmp/requirements.txt"]

RUN ["pip3", "install", "-r", "/tmp/requirements.txt"]

COPY ["src/", "/opt/app_aggregator"]

WORKDIR "/opt/app_aggregator"

ENTRYPOINT ["python3.10", "-u", "main.py"]
