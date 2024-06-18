# syntax = docker/dockerfile:1.5
FROM python:3.10-slim

WORKDIR /senbot

RUN apt update && \
    apt install -y poppler-utils && \
    apt clean all

COPY requirements.txt /senbot

RUN --mount=type=cache,target=/root/.cache/pip cd /senbot && pip install -r requirements.txt --cache-dir /root/.cache/pip

COPY . /senbot

EXPOSE 5000

VOLUME /root/.cache

# Specify the command to run on container start
CMD ["python3", "/senbot/main.py"]
