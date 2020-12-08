FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y openssh-server cron sudo python3 python3-pip && \
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
    chmod g+w exam .local && \
    echo sudo /bin/isolate.sh >> .bashrc && \
    echo exit >> .bashrc

COPY root /root/
COPY sshd_config /etc/ssh/sshd_config
COPY sudoers /etc/sudoers
COPY isolate.sh /bin/isolate.sh

RUN chmod +x /root/entrypoint.sh && \
    chmod +x /bin/isolate.sh && \
    ln -sf /dev/null /root/.bash_history && \
    chmod 440 /etc/sudoers && \
    chmod o-r /tmp && \
    mkdir -p /tmp/s3cret_d1r_fed14cdf/exam && \
    chmod -R 775 /tmp/s3cret_d1r_fed14cdf

EXPOSE 22

ENTRYPOINT ["/root/entrypoint.sh"]
