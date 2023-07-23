FROM ubuntu:22.04

RUN apt-get update && \
        apt-get install software-properties-common -y && \
        add-apt-repository ppa:deadsnakes/ppa -y && \
        apt-get update && \
        apt-get install -y --no-install-recommends python3.10 python3-pip python3-dev libssl-dev

RUN python3.10 --version

COPY ["requirements.txt", "/tmp/requirements.txt"]

RUN ["pip3", "install", "-r", "/tmp/requirements.txt"]

COPY ["src/", "/opt/app_server"]

WORKDIR "/opt/app_server"

ENTRYPOINT ["python3.10", "-m", "uvicorn", "--host", "0.0.0.0", "main:app"]
