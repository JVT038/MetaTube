FROM phusion/passenger-full:2.0.1
ENV PORT 5000
ENV FFMPEG /usr/bin
EXPOSE ${PORT}
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
    pip3 install -r MetaTube/requirements.txt
# CMD ["/usr/bin/sh"]
CMD ["/usr/bin/python3", "MetaTube/metatube.py"]