############################################################
# Dockerfile to build the BAM filtering step in the ENCODE 
# Mapping ChIP-seq pipeline container image
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
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    python-dev \
    python-setuptools \
    ant \
    openjdk-7-jdk

# Install pip and python packages: common and python-dateutils
RUN easy_install pip
RUN pip install common
RUN pip install python-dateutil

RUN mkdir image_software

# Install samtools 0.1.19
RUN cd /image_software && git clone --branch 0.1.19 https://github.com/samtools/samtools.git
RUN cd /image_software/samtools && make && cp /image_software/samtools/samtools /usr/local/bin/samtools

# Install bedtools 2.26.0
RUN cd /image_software && git clone --branch v2.26.0 https://github.com/arq5x/bedtools2.git
RUN cd /image_software/bedtools2 && make && cp -a /image_software/bedtools2/bin/. /usr/local/bin/

# Install picard 1.92
RUN cd /image_software && git clone --branch 1.92 https://github.com/broadinstitute/picard.git
RUN cd /image_software/picard && ant -Ddist=/picard -lib lib/ant package-commands

# Get ENCODE pipeline container repository
RUN cd /image_software && git clone https://github.com/ENCODE-DCC/pipeline-container.git
RUN cd /image_software/pipeline-container && git fetch && git pull

ENTRYPOINT ["python", "/image_software/pipeline-container/src/filter_qc.py"]