FROM python:3.11.4-bookworm
ARG EXPORT_PORT
ENV port $EXPORT_PORT
ARG DIRECTORY_BASE
ENV directory $DIRECTORY_BASE
RUN apt update &&\
    apt install -y \
    python3-dev default-libmysqlclient-dev build-essential libssl-dev libffi-dev python3-setuptools && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/app

COPY $directory ./

COPY ./deploy/script.sh ./

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE $EXPORT_PORT

RUN ["chmod", "+x", "./script.sh"]

RUN echo "/bin/bash /usr/app/script.sh $port" > /tmp.sh

RUN ["chmod", "+x", "/tmp.sh"]

ENTRYPOINT ["/bin/bash", "/tmp.sh"]