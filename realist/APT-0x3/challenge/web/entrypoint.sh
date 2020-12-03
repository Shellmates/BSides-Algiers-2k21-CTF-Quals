#!/bin/bash

# Restore the original database every 30 minutes
echo '*/30 * * * * cp /root/db.sqlite /app/db.sqlite' | crontab -

# Backup database
cp /app/db.sqlite /root

# Start job scheduler
service cron start

su ctf -c "python3 app.py"
