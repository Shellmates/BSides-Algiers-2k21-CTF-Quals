#!/bin/sh

EXEC="/root/openssl.py"
PORT=1337

socat tcp-l:$PORT,reuseaddr,fork,keepalive exec:"$EXEC",stderr
