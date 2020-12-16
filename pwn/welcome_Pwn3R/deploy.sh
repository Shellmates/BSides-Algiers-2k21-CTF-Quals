#!/bin/sh

docker build --tag=pwn/welcome_pwn3r . && \
  docker run -d -p 1337:1337 --rm --name=welcome_pwn3r -it pwn/welcome_pwn3r
