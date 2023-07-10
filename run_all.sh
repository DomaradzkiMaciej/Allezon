for i in $(seq -w 01 10); do
    sshpass -p $1 ssh st108@st108vm1$i.rtb-lab.pl -o StrictHostKeyChecking=no -C "/bin/true";
    echo "Done"
done

sudo apt -y install ansible sshpass

cd ansible || exit

ansible-playbook -i ./hosts --extra-vars "ansible_user=st108 ansible_password=$1" docker-playbook.yaml
ansible-playbook -i ./hosts --extra-vars "ansible_user=st108 ansible_password=$1" swarm-playbook.yaml
ansible-playbook -i ./hosts --extra-vars "ansible_user=st108 ansible_password=$1" aerospike-playbook.yaml

cd .. || exit

DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
sudo mkdir -p $DOCKER_CONFIG/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/download/v2.19.1/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
sudo chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

export PATH=~/usr/local/bin:$PATH

sudo docker service create --name registry -p 5000:5000 registry:2
sudo docker node update --label-add haproxy=true $(hostname)
sudo docker-compose build
sudo docker-compose push
sudo docker stack deploy --compose-file docker-compose.yml allezone