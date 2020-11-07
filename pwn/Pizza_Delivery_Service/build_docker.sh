#!/bin/sh

docker build --tag=pwn/pizza_delivery_service .
docker run -d -p 1337:1337 --rm --name=Pizza_Delivery_Service -it pwn/pizza_delivery_service
