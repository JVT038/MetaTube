FROM phusion/passenger-full:2.0.1
LABEL Author JVT038
LABEL Maintainer JVT038
ENV PORT 5000
ENV FFMPEG /usr/bin
ENV DOWNLOADS /MetaTube/downloads
EXPOSE $PORT
VOLUME /MetaTube
RUN \
    echo "**** Installing build packages ****" && \
    apt-get update && \
    apt-get install -y \
        git \
        python3-pip \
        ffmpeg && \
    echo "**** Installing Python packages ****" && \
    git clone https://github.com/JVT038/MetaTube.git && \
    mkdir -p /config && \
    mv MetaTube/* /config && \
    pip3 install -r /config/requirements.txt && \
    mkdir -p $DOWNLOADS

CMD ["/usr/bin/python3", "config/metatube.py"]