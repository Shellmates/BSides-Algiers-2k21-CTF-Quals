#!/bin/bash

export SSHPASS="m@rge1sl1f3"

sshpass -e sftp -oStrictHostKeyChecking=no -oBatchMode=no -b - sftp@homer << END
   get -r /tmp/s3cret_d1r_fed14cdf/exam /home/marge/exam
   bye
END

cd /home/marge
for archive in ./exam/*.pth; do
    (/root/model_loader.py "$archive") &
done

sleep 10
rm -rf ./exam
