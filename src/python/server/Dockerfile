# syntax=docker/dockerfile:1
FROM python:3
RUN apt-get update

WORKDIR /app
COPY . .
RUN mkdir source
EXPOSE 12345
VOLUME [ "/app/source" ]
ENV SOURCE_TYPE="local" REMOTE_SOURCE="None" BUFFSIZE="1024" HASH_ALGORITHM="md5"

ENTRYPOINT python ./server.py -t ${SOURCE_TYPE} -r ${REMOTE_SOURCE} -b ${BUFFSIZE} -h ${HASH_ALGORITHM}
