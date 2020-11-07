#!/bin/sh

EXEC="./pizza-service"
PORT=1337

socat tcp-l:$PORT,reuseaddr,fork,keepalive exec:"$EXEC",stderr
