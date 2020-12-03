FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y cron python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN useradd -s /bin/bash ctf
RUN mkdir /app

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

WORKDIR /app
COPY app .

RUN chown -R ctf:ctf .

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
