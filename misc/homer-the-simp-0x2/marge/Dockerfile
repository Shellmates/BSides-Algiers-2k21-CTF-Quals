FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y cron python3 sshpass openssh-client && \
    rm -rf /var/lib/apt/lists/*
    
RUN useradd -m -s /bin/bash marge

WORKDIR /home/marge

COPY challenge .

RUN ln -sf /dev/null .bash_history && \
    chown -R root:root .

COPY root /root/

RUN chmod +x /root/script.sh && \
    chmod +x /root/entrypoint.sh && \
    chmod +x /root/model_loader.py && \
    ln -sf /dev/null /root/.bash_history

ENTRYPOINT ["/root/entrypoint.sh"]
