FROM python:3.9-slim-buster

# copy files
WORKDIR /opt/install
COPY . .

# install unix dependencies
RUN apt-get update
RUN apt-get install -y g++

# install python packages
RUN python -m pip install --upgrade pip
RUN python -m pip install .

# clean up
RUN apt-get remove -y g++
RUN apt-get autoremove -y
RUN apt-get clean

# set project dir
WORKDIR /opt/project
RUN rm -rfd /opt/install
