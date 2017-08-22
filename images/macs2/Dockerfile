############################################################
# Dockerfile to build the signal track generation step in the 
# ENCODE Peaks ChIP-seq pipeline container image
# Based on Ubuntu 14.04
############################################################

# Set the base image to Ubuntu 14.04
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Otto Jolanki

# Update the repository sources list
# Install base packages: git, python, wget, unzip, R
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libboost-dev \
    libncurses5-dev \
    libncursesw5-dev \
    python-dev \
    python-setuptools \
    zlib1g-dev \
    unzip \
    wget \
    python-numpy
# Install pip and python packages: common, python-dateutils, python-magic 
RUN easy_install pip
RUN pip install common
RUN pip install python-dateutil
RUN pip install -U --no-deps MACS2
RUN pip install python-magic

# Wget more tools 
RUN wget http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/bedClip
RUN wget http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/bedToBigBed
RUN wget http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/bedGraphToBigWig

RUN chmod 755 bedClip && mv bedClip /usr/bin/
RUN chmod 755 bedToBigBed && mv bedToBigBed /usr/bin/
RUN chmod 755 bedGraphToBigWig && mv bedGraphToBigWig /usr/bin/

RUN mkdir /image_software
WORKDIR /image_software

# Install bedtools 2.26.0
RUN git clone --branch v2.26.0 https://github.com/arq5x/bedtools2.git
RUN cd bedtools2 && make && make install

# Get ENCODE pipeline container repository
# This COPY asumes the build context is the root of the pipeline-container repo
# and it gets whatever is checked out plus local modifications
RUN mkdir pipeline-container
COPY / pipeline-container

# Set up the user directory
RUN groupadd -r encode && useradd --no-log-init -r -m -d /home/encode/ -g encode encode
USER encode
WORKDIR /home/encode

ENTRYPOINT ["python", "/image_software/pipeline-container/src/macs2.py"]
