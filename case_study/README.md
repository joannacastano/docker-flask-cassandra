# Simple Todo app with authentication using Flask and CassandraDB

## To run this app in a docker network, you will need:

- [x] Install [Docker](https://docs.docker.com/get-docker/) on your machine
- [x] Pull latest CassandraDB image 
```
docker pull cassandra:latest
```
- [x] Create a docker network
```
docker network create <network name> 
```
- [x] Run Cassandra container in your created network
```
docker run -d --name cassandra --hostname cassandra --network <network name> cassandra  
```
- [x] Create the 'todoapp' keyspace in the Cassandra container 
```
docker exec -it $(docker ps -qf "name=^cassandra$") cqlsh -c "CREATE KEYSPACE IF NOT EXISTS keyspace_name WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};"
```
NOTE: The ' docker ps -qf "name=^cassandra$" ' command finds the container_id of a ' cassandra ' container.

- [x] Pull this flask app's image 
```
docker pull joannacastano05/flask_app:latest 
```
- [x] Run this flask app in the same network
```
docker run -d --name <flask container name> --network <network name> -p 8000:5000 joannacastano05/flask_app:latest
```
NOTE: I am binding this container's port 5000 (default of flask) to my local's port 8000.
- [x] View app by going to localhost:8000

## Have fun playing around!
