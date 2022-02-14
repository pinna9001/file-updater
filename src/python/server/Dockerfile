# syntax=docker/dockerfile:1
FROM python:3
RUN apt-get update

WORKDIR /app
COPY . .
RUN mkdir source
EXPOSE 12345
VOLUME [ "/app/source" ]

ENTRYPOINT python ./server.py
