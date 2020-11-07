FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y socat && \
    rm -rf /var/lib/apt/lists/*

RUN useradd ctf && \
    mkdir /challenge

COPY challenge /challenge

WORKDIR /challenge

RUN chmod +x run_server.sh pizza-service && \
    chown -R root:root .

EXPOSE 1337

USER ctf

ENTRYPOINT ["./run_server.sh"]
