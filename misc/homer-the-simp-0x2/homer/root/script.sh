#!/bin/bash

# transfer the files 10sec before the cron job on the other
# container runs
sleep 50
rm -f /tmp/s3cret_d1r_fed14cdf/exam/*
for filepath in /tmp/tmp.*/exam/*.pth; do
    tmpname=$(basename $(mktemp -u))
    filename=$(basename "$filepath")
    cp -p "$filepath" "/tmp/s3cret_d1r_fed14cdf/exam/${tmpname}_${filename}"
done
