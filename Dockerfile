FROM golang:1.25.0-bookworm AS mc-buider

RUN go install github.com/minio/mc@latest


FROM python:3.12.4-slim-bookworm

WORKDIR /app

COPY --from=mc-buider /go/bin/mc /usr/local/bin/mc
COPY dl.py .

RUN python3 -m pip install -U "yt-dlp[default]"
RUN apt-get update && \
    apt-get install -y yt-dlp ffmpeg curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD [ "python3", "/app/dl.py" ]
