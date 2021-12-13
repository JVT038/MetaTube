FROM phusion/passenger-full:2.0.1
LABEL Author=JVT038 \
    Maintainer=JVT038 \
    Name=MetaTube
ENV PORT=5000 \
    FFMPEG=/usr/bin \
    DOWNLOADS=/downloads
EXPOSE $PORT
COPY . /config/
RUN \
    echo "**** Installing build packages ****" && \
    apt-get update && \
    apt-get install -y \
        git \
        python3-pip \
        ffmpeg && \
    echo "**** Installing Python packages ****" && \
    mkdir -p /config && \
    mv MetaTube/* /config && \
    pip3 install -r /config/requirements.txt && \
    mkdir -p $DOWNLOADS

ENTRYPOINT ["/usr/bin/python3", "config/metatube.py"]