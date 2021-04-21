#!/bin/bash

echo '######## Docker dev machine status ########'
docker-machine status dev 2> /dev/null || docker-machine create -d virtualbox dev
eval $(docker-machine env dev)
docker-machine ls

echo '######## Building and running ########'
docker-compose up --build -d
docker-compose ps

echo '######## IP address ########'
docker-machine ip dev

echo '######## Attaching to logs ########'
docker-compose logs --f web