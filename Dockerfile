FROM python:3.10.10

WORKDIR /server

COPY ./server/requirements.txt /server/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /server/requirements.txt

COPY ./server /server
