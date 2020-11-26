FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y openssh-server cron python3 python3-pip && \
    pip3 install notebook && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /srv/sftp && \
    useradd -m -s /bin/bash homer && \
    useradd -d /home/homer -s /usr/sbin/nologin sftp && \
    echo 'sftp:m@rge1sl1f3' | chpasswd

WORKDIR /home/homer

COPY challenge .

RUN ln -sf /dev/null .bash_history && \
    mkdir exam .local && \
    chown -R root:homer . && \
    chown root:root . && \
    chmod 440 flag.txt && \
    chmod g+w exam .local

COPY root /root/
COPY sshd_config /etc/ssh/sshd_config

RUN chmod +x /root/entrypoint.sh && \
    ln -sf /dev/null /root/.bash_history

EXPOSE 22

ENTRYPOINT ["/root/entrypoint.sh"]