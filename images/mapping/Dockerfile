############################################################
# Dockerfile to build the mapping with BWA step in 
# the ENCODE Mapping ChIP-seq pipeline container image
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Idan Gabdank

# Update the repository sources list
# Install base packages: java, git, wget, python
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    git \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    python-dev \
    python-setuptools \
    openjdk-8-jdk

RUN mkdir image_software

# Install Trimmomatic 0.36
RUN cd /image_software && wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.36.zip
RUN cd /image_software && unzip Trimmomatic-0.36.zip && cd Trimmomatic-0.36 && ls

# Install BWA 0.7.10
RUN cd /image_software && mkdir bwa_0_7_10
RUN cd /image_software/bwa_0_7_10 && git clone --branch 0.7.10 https://github.com/lh3/bwa.git
RUN cd /image_software/bwa_0_7_10/bwa && make

# Get ENCODE pipeline container repository
ARG COMMIT=none
ARG BRANCH=master
RUN cd /image_software && git clone --branch $BRANCH https://github.com/ENCODE-DCC/pipeline-container.git
RUN cd /image_software/pipeline-container && git fetch && git pull

ENTRYPOINT ["python", "/image_software/pipeline-container/src/encode_map.py"]
