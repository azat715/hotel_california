# syntax = docker/dockerfile:1.3
FROM python:3.9-alpine

RUN apk update 
# добавляю для wait-for-it.sh
RUN apk add --no-cache bash

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN --mount=type=cache,target=/root/.cache \
    apk add --no-cache --virtual .build-deps build-base gcc musl-dev libffi-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps
COPY . /code/