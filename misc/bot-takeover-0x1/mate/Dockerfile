FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install discord python-dotenv bcrypt validators && \
    rm -rf /var/lib/apt/lists/*

RUN useradd mate

COPY entrypoint.sh /

COPY app /app

WORKDIR /app

RUN chmod +x matebot.py && \
    chown -R mate:mate . && \
    chmod +x /entrypoint.sh

USER mate

ENTRYPOINT ["/entrypoint.sh"]
