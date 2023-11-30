
FROM pytorch/pytorch:1.9.0-cuda10.2-cudnn7-runtime

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y python3-opencv

WORKDIR /senbot

EXPOSE 5000
# Specify the command to run on container start
CMD ["python", "main.py"]
