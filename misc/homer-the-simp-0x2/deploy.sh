#!/bin/bash

# Build images
docker build --tag=homer-the-simp/homer:1.0 ./homer
docker build --tag=homer-the-simp/marge:1.0 ./marge

docker-compose --compatibility up -d
