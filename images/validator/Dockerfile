############################################################
# Dockerfile to build output validator 
# Based on Ubuntu 14.04
############################################################

# Set the base image to Ubuntu 14.04
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Idan Gabdank

# Update the repository sources list
# Install base packages: git, python, java
RUN apt-get update && apt-get install -y \
    git \
    python

# Requirements for setting up cwltool
RUN apt-get install -qqy --force-yes \
    python-dev \
    python-setuptools \
    python-requests \
    python-yaml \
    python-lockfile \
    python-pyparsing \
    awscli 

RUN easy_install pip


# Requirements for setting up cwltool
RUN pip install setuptools --upgrade
RUN pip install ruamel.yaml==0.13.4 cwltool==1.0.20161227200419 dynamoq tractorbeam

RUN mkdir image_software
WORKDIR /image_software

# Get ENCODE pipeline container repository
# This COPY asumes the build context is the root of the pipeline-container repo
# and it gets whatever is checked out plus local modifications
RUN mkdir pipeline-container && cd pipeline-container && mkdir src
COPY /src/validate_output.pyc pipeline-container/src/validate_output.pyc

ENTRYPOINT ["python", "/image_software/pipeline-container/src/validate_output.pyc"]