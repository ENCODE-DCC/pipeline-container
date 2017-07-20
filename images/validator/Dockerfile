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

RUN mkdir image_software
WORKDIR /image_software

# Get ENCODE pipeline container repository
ARG COMMIT=none
ARG BRANCH=master
RUN git clone --branch $BRANCH https://github.com/ENCODE-DCC/pipeline-container.git

ENTRYPOINT ["python", "/image_software/pipeline-container/src/validate_output.py"]