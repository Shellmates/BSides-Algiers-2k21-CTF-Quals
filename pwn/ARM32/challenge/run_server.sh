#!/bin/sh

export QEMU_LD_PREFIX=/usr/arm-linux-gnueabihf/
EXEC="qemu-arm-static ./arm32"
PORT=1337

socat tcp-l:$PORT,reuseaddr,fork,keepalive exec:"$EXEC",stderr
