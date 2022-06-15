# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app
COPY ./mundobot_env/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y ffmpeg
COPY ./mundobot_env .

CMD [ "python3", "-m", "mundobot.mundobot" ]

