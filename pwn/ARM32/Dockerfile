FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y gcc-arm-linux-gnueabihf libc6-dev-armhf-cross qemu-user-static && \
    apt-get install -y socat && \
    rm -rf /var/lib/apt/lists/*

RUN useradd ctf && \
    mkdir /challenge

COPY challenge /challenge

WORKDIR /challenge

RUN chmod +x run_server.sh arm32 && \
    chown -R root:root .

EXPOSE 1337

USER ctf

ENTRYPOINT ["./run_server.sh"]
