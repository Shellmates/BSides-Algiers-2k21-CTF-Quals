#!/bin/bash

USER="homer"

crontab /root/cron.tab
service cron start
service ssh start
cd "/home/$USER/deep-learning"
while :; do
    su "$USER" -c "jupyter notebook --no-browser"
done
