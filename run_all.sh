#! /bin/bash

student=$1
pass=$2

if [ $# -ne 2 ]; then
    echo "Usage: $0 <student> <pass>"
    exit 1
fi

sudo apt -y install sshpass docker ansible
sudo add-apt-repository -y ppa:ansible/ansible
sudo apt update
sudo apt -y upgrade ansible

for i in $(seq -w 01 10); do
    sshpass -p $pass ssh "$student"@"$student"vm1"$i".rtb-lab.pl -o StrictHostKeyChecking=no -C "/bin/true";
    echo "Done"
done

cd app_ansible || exit

sed "s/_student_/$student/g" hosts.template > hosts

ansible-playbook -i ./hosts --extra-vars "ansible_user=$student ansible_password=$pass" registry-playbook.yaml
ansible-playbook -i ./hosts --extra-vars "ansible_user=$student ansible_password=$pass" docker-playbook.yaml
ansible-playbook -i ./hosts --extra-vars "ansible_user=$student ansible_password=$pass" swarm-playbook.yaml
ansible-playbook -i ./hosts --extra-vars "ansible_user=$student ansible_password=$pass" aerospike-playbook.yaml
ansible-playbook -i ./hosts --extra-vars "ansible_user=$student ansible_password=$pass ansible_ssh_extra_args='-o StrictHostKeyChecking=no'" kafka-playbook.yaml

cd .. || exit

source ./run_docker.sh