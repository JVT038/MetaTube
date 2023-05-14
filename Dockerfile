FROM python:3.9-alpine
LABEL Author=JVT038 \
    Maintainer=JVT038 \
    Name=MetaTube
ENV PORT=5000 \
    FFMPEG=/usr/bin \
    DOWNLOADS=/downloads \ 
    DATABASE_URL=sqlite:////database/app.db \
    FLASK_APP=/app/metatube.py
EXPOSE $PORT
COPY --chmod=0755 . /app
RUN \
    mv /app/migrations /migrations && \
    apk update && \
    apk add --no-cache --upgrade alpine-sdk libffi-dev ffmpeg libmagic && \
    mkdir -p {/app,$DOWNLOADS,/database} && \
    python3 -m pip install --upgrade pip && \
    pip3 install -r /app/requirements.txt && \
    apk del --purge alpine-sdk
    

# ENTRYPOINT ["/usr/local/bin/python3", "app/metatube.py"]
ENTRYPOINT ["app/entrypoint.sh"]