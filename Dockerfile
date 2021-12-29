# FROM phusion/passenger-full:2.0.1
FROM alpine:3.15
LABEL Author=JVT038 \
    Maintainer=JVT038 \
    Name=MetaTube
ENV PORT=5000 \
    FFMPEG=/usr/bin \
    DOWNLOADS=/downloads
EXPOSE $PORT
COPY . /config/
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        py-gevent \
        ffmpeg \
        gcc \
        musl-dev \
        libffi-dev \
        openssl-dev && \
    mkdir -p /config && \
    pip3 install -r /config/requirements.txt && \
    mkdir -p $DOWNLOADS

ENTRYPOINT ["/usr/bin/python3", "config/metatube.py"]