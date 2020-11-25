#!/bin/bash

export SSHPASS="m@rge1sl1f3"

sshpass -e sftp -oStrictHostKeyChecking=no -oBatchMode=no -b - sftp@homer << END
   get -r exam /home/marge/
   bye
END

cd /home/marge/exam
for archive in ./*.pth; do
    /root/model_loader.py "$archive"
done
