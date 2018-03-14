FROM ubuntu:16.04
MAINTAINER Jeffery Do <timithy4569@gmail.com>

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/flaskapp/src
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    apt-utils \
    build-essential \
    ca-certificates \
    gcc \
    git \
    libpq-dev \
    make \
    python-pip \
    python2.7 \
    python2.7-dev \
    ssh \
    && apt-get autoremove \
    && apt-get clean
# We copy the requirements.txt file first to avoid cache invalidations
COPY requirements.txt /opt/services/flaskapp/src/
WORKDIR /opt/services/flaskapp/src
RUN apt-get install -y libblas3 liblapack3 libstdc++6 python-setuptools
RUN pip install -r requirements.txt
COPY . /opt/services/flaskapp/src
