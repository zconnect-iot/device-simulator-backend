#! /bin/bash -e

docker build -f Dockerfile.stretch.zcsimbase -t zcsimbase:latest .
.env/bin/docker-compose build
.env/bin/docker-compose up
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls --format '{{.Name}}')
