FROM ubuntu:18.04
RUN apt update -y && apt install -y libb64-0d libb64-dev libssl1.1 socat && apt clean
ADD solution/flag.txt solution/SHmAc_key /
WORKDIR /app
ADD SHmAc SHmAc.c ./
ENTRYPOINT ["socat","-dd","TCP4-LISTEN:9000,fork,reuseaddr","EXEC:/app/SHmAc,pty,echo=0,raw,iexten=0"]
