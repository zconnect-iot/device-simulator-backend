#! /bin/bash

docker build -f Dockerfile.zcsimbase -t zcsimbase:latest .
docker-compose build
docker-compose up
