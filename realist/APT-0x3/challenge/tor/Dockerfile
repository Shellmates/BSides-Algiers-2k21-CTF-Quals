FROM alpine:latest

RUN apk update && \
    apk add tor \
    --update-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ && \
    rm -rf /var/cache/apk/*

COPY torrc /etc/tor/torrc
COPY onion /var/lib/tor/hidden_service

RUN chown -R tor \
    /var/lib/tor/hidden_service \ 
    /etc/tor \
    && chmod 0700 /var/lib/tor/hidden_service

USER tor

ENTRYPOINT ["tor", "-f", "/etc/tor/torrc"]
