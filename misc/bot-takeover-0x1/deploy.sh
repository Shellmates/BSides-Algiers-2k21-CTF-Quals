#!/bin/sh

docker build --tag=bot-takeover/mate ./mate && \
  docker build --tag=bot-takeover/openssl ./openssl && \
    docker-compose --compatibility up -d
