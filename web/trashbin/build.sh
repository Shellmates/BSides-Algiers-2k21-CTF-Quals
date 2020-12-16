#!/bin/bash

docker build --tag=trashbin .
docker run -it --rm -p8080:8080 --name=trashbin trashbin:latest
