#! /bin/bash

pass=$1
student=$2

if [ $# -ne 2 ]; then
    echo "Usage: $0 <password> <student>"
    exit 1
fi
 
for i in $(seq -w 01 10); do
    sshpass -p $pass ssh "$student"@"$student"vm1"$i".rtb-lab.pl -o StrictHostKeyChecking=no -C "/bin/true";
    echo "Done"
done

sudo apt -y install ansible sshpass

cd app_ansible || exit

sed "s/_student_/$student/g" hosts.template > hosts

ansible-playbook -i ./hosts --extra-vars "ansible_user=$student ansible_password=$pass" registry-playbook.yaml
ansible-playbook -i ./hosts --extra-vars "ansible_user=$student ansible_password=$pass" docker-playbook.yaml
ansible-playbook -i ./hosts --extra-vars "ansible_user=$student ansible_password=$pass" swarm-playbook.yaml
ansible-playbook -i ./hosts --extra-vars "ansible_user=$student ansible_password=$pass" aerospike-playbook.yaml

cd .. || exit

source ./run_docker.sh