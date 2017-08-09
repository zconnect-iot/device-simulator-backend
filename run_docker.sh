#! /bin/bash -e

docker build -f Dockerfile.stretch.zcsimbase -t zcsimbase:latest .
docker-compose build
docker-compose up
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls --format '{{.Name}}')
