FROM python:3.9-alpine
LABEL Author=JVT038 \
    Maintainer=JVT038 \
    Name=MetaTube
ENV PORT=5000 \
    FFMPEG=/usr/bin \
    DOWNLOADS=/downloads \ 
    DATABASE_URL=sqlite:////database/app.db
EXPOSE $PORT
COPY . /config/
RUN \
    apk update && \
    apk add -t build-deps --no-cache python3-dev libffi-dev gcc musl-dev make file && \
    apk add --no-cache ffmpeg libmagic && \
    mkdir -p /config && \
    python3 -m pip install --upgrade pip && \
    pip3 install -r /config/requirements.txt && \
    apk del --purge build-deps && \
    mkdir -p $DOWNLOADS

ENTRYPOINT ["/usr/local/bin/python3", "config/metatube.py"]
