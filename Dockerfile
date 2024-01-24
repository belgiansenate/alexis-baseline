FROM python:3.10-slim

WORKDIR /senbot

COPY requirements.txt /senbot

RUN cd /senbot && apt update && \
    apt install -y poppler-utils

RUN cd /senbot && pip install pdf2text

RUN cd /senbot && pip install -r requirements.txt

COPY . /senbot

# Specify the command to run on container start
CMD ["python3", "/senbot/main.py"]
