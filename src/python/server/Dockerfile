# syntax=docker/dockerfile:1
FROM python:3
RUN apt-get update

WORKDIR /app
COPY . .
RUN mkdir source
EXPOSE 12345
VOLUME [ "/app/source" ]
ENV SOURCE_TYPE="local" REMOTE_SOURCE="None" BUFFSIZE="1024" HASH_ALGORITHM="md5"
    
ENTRYPOINT python ./server.py ${SOURCE_TYPE} ${REMOTE_SOURCE} ${BUFFSIZE} ${HASH_ALGORITHM} 