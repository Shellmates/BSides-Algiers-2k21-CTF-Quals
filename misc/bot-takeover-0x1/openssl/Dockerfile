FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y python3 python3-pip openssl socat && \
    pip3 install python-dotenv && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -s /bin/bash mate

COPY root /root

COPY app /app

COPY entrypoint.sh /root/

RUN chmod +x /root/entrypoint.sh && \
    chmod +x /root/openssl.py && \
    chmod +x /app/matebot.py
    
ENTRYPOINT ["/root/entrypoint.sh"]
