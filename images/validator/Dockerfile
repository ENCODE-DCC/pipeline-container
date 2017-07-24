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
# This COPY asumes the build context is the root of the pipeline-container repo
# and it gets whatever is checked out plus local modifications
RUN mkdir pipeline-container && cd pipeline-container && mkdir src
COPY /src/validate_output.pyc pipeline-container/src/validate_output.pyc

ENTRYPOINT ["python", "/image_software/pipeline-container/src/validate_output.pyc"]