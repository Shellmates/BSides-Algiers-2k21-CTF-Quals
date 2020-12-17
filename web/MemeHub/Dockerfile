FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY entrypoint.sh /
RUN chmod +x entrypoint.sh

RUN useradd -s /bin/bash ctf
RUN mkdir /app

WORKDIR /app
COPY app .

RUN chown -R ctf:ctf uploads/

EXPOSE 8080

USER ctf

ENTRYPOINT ["/entrypoint.sh"]
