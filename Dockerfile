FROM python:3.10-slim 

WORKDIR /senbot

COPY requirements.txt /senbot

RUN apt update && apt install build-essential -y &&  \
    apt install libpoppler-cpp-dev -y  && \
    apt install pkg-config -y

RUN cd /senbot && \
    pip install cmake && \
    pip install --use-pep517 python-poppler

RUN cd /senbot && pip install -r requirements.txt

COPY . /senbot

EXPOSE 5000
# Specify the command to run on container start
CMD ["python", "/senbot/main.py"]
