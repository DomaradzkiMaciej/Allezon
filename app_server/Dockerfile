FROM debian:bullseye-slim

RUN apt-get update && \
	apt-get install -y --no-install-recommends python3 python3-pip python3-dev libssl-dev

COPY ["requirements.txt", "/tmp/requirements.txt"]

RUN ["pip3", "install", "-r", "/tmp/requirements.txt"]

COPY ["src/", "/opt/app_server"]

WORKDIR "/opt/app_server"

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "main:app"]