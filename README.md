# Allezon
This repository contains a platform implementing use cases 1 & 2  for Practical distributed systems class's assignement.

## Deployment
To deploy this project on nodes shared by RTB House just change servers names in repository and run ./run_all.sh <student> <password>.

## Architecture overview
This solution consist of 4 nodes running Aerospike and 6 nodes with server instances ballanced by HAProxy.

# Database
Database is an Aerospike Cluster consisting of 4 nodes with replication factor 2.

# Load Balancer
Request are ballances by HAProxy, which automaticly detect server's instances created by Docker Compose.

# Server
Server instance is a single-threaded FastApi application. The distribution of instances on nodes in managed by Docker Composes (12 replicas and max 4 replicas per node).
