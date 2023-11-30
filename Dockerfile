
FROM pytorch/pytorch:1.9.0-cuda10.2-cudnn7-runtime

COPY ./requirements.txt /install/requirements.txt

RUN pip install -r /install/requirements.txt

WORKDIR /code
# Specify the command to run on container start
CMD ["python", "main.py"]
