FROM python:3.12-alpine
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
    apk add --no-cache --upgrade alpine-sdk libffi-dev ffmpeg libmagic && \
    mkdir -p {/config,$DOWNLOADS,/database} && \
    python3 -m pip install --upgrade pip && \
    pip3 install --no-cache-dir -r /config/requirements.txt && \
    apk del --purge alpine-sdk
ENTRYPOINT ["/usr/local/bin/python3", "config/metatube.py"]
