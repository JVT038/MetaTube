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
    apk add --no-cache python3-dev libffi-dev gcc musl-dev make ffmpeg libmagic && \
    mkdir -p /config && \
    pip3 install -r /config/requirements.txt && \
    apk del --purge python3-dev libffi-dev gcc musl-dev make && \
    mkdir -p $DOWNLOADS

ENTRYPOINT ["/usr/local/bin/python3", "config/metatube.py"]
