#!/bin/sh

docker build --tag=pwn/arm32 . && \
  docker run -d -p 1337:1337 --rm --name=ARM32 -it pwn/arm32
