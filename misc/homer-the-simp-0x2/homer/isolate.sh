#!/bin/bash

tmpdir=$(mktemp -du)
cp -rp /home/homer $tmpdir
head -n -2 /home/homer/.bashrc > $tmpdir/.bashrc
/usr/bin/unshare -m --propagation unchanged bash -c "mount --bind $tmpdir /home/homer/ && su - homer"
