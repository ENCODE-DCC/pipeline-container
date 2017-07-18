############################################################
# Dockerfile to build the mapping with BWA step in 
# the ENCODE Mapping ChIP-seq pipeline container image
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Idan Gabdank

# Update the repository sources list
# Install base packages: java, git, wget, python
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libncurses5-dev \
    libncursesw5-dev \
    python-dev \
    python-setuptools \
    unzip \
    wget \
    zlib1g-dev

RUN mkdir /image_software
WORKDIR /image_software

# Install Trimmomatic 0.36
RUN wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.36.zip
RUN unzip Trimmomatic-0.36.zip && ls Trimmomatic-0.36

# Install BWA 0.7.10
RUN git clone --branch 0.7.10 https://github.com/lh3/bwa.git
RUN cd bwa && make && cp bwa /usr/local/bin/

# Set up the user directory
RUN groupadd -r encode && useradd --no-log-init -r -g encode encode
WORKDIR ~encode
# Get ENCODE pipeline container repository
ARG COMMIT=none
ARG BRANCH=fix_samtools_versions
RUN git clone --branch $BRANCH https://github.com/ENCODE-DCC/pipeline-container.git
RUN cd pipeline-container && git fetch && git pull

ENTRYPOINT ["python", "pipeline-container/src/encode_map.py"]
