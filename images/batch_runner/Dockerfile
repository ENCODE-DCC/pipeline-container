############################################################
# Dockerfile to build image that runs CWL defined ENCODE 
# Mapping Chip-seq Pipeline on AWS batch using Aegea
# (https://github.com/kislyuk/aegea)
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Ulugbek Baymuradov

# Update the repository sources list
# Install base packages: git, python
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-{pip,dev,cffi} \
    libffi-dev \
    libssl-dev \
    moreutils

# Install cwl-runner
RUN pip install cwlref-runner

# Install aegea
RUN pip install aegea

# Get ENCODE pipeline container repository
# This COPY asumes the build context is the root of the pipeline-container repo
# and it gets whatever is checked out plus local modifications
RUN mkdir pipeline-container
COPY / pipeline-container

# Set up the user directory
RUN groupadd -r encode && useradd --no-log-init -r -m -d /home/encode/ -g encode encode
USER encode
WORKDIR /home/encode

ENTRYPOINT ["python", "/image_software/pipeline-container/src/encode_post_map.py"]
