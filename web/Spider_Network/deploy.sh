#!/bin/bash

docker build --tag=web/spider_network .
docker run -d -p 8000:80 --rm --name=spider_network -it web/spider_network
