#!/bin/sh

EXEC="./l33t-club"
PORT=1337

socat tcp-l:$PORT,reuseaddr,fork,keepalive exec:"$EXEC",stderr
