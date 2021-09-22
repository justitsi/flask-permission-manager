FROM python:3.9-alpine

# setup production python env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependecies
RUN pip install --upgrade pip
RUN apk --no-cache --update upgrade
RUN apk add musl-dev gcc rust cargo python3-dev openssl-dev postgresql-dev libffi-dev py3-virtualenv alpine-sdk
RUN mkdir /project
WORKDIR /project

# setup static files (startup script)
COPY ./static_files/startup.sh /project/startup.sh
RUN chmod +x /project/startup.sh

# setup project - install requirements and copy source code and certs
COPY requirements.txt /project/
RUN pip3 install -r requirements.txt
COPY ./src /project/src

# Clear development .env and copy production environment settings to container
RUN rm /project/src/.env
COPY ./static_files/prod.env /project/src/.env

# set entrypoint
CMD ["./startup.sh"]