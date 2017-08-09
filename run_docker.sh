#! /bin/bash

docker build -f Dockerfile.stretch.zcsimbase -t zcsimbase:latest .
docker-compose build
docker-compose up
