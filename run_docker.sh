#! /bin/bash

# DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
# sudo mkdir -p $DOCKER_CONFIG/cli-plugins
# sudo curl -SL https://github.com/docker/compose/releases/download/v2.19.1/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
# sudo chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# export PATH=~/usr/local/bin:$PATH

# sudo docker service create --name registry -p 5000:5000 registry:2

for i in $(seq -w 01 06); do
    sudo docker node update --label-add s"$i"=true st108vm1"$i"
done

sudo docker node update --label-add haproxy=true $(hostname)
sudo docker compose build
sudo docker compose push
sudo docker stack deploy --compose-file docker-compose.yml allezon