#!/bin/sh

docker container stop memehub
docker build --tag=web/memehub .
docker run -d -p 4455:8080 --rm --name=memehub -it web/memehub
