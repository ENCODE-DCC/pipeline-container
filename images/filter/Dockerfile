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
    ant \
    build-essential \
    git \
    libncurses5-dev \
    libncursesw5-dev \
    openjdk-7-jdk \
    python-dev \
    python-setuptools \
    wget \
    zlib1g-dev

# Install pip and python packages: common and python-dateutils
RUN easy_install pip
RUN pip install common
RUN pip install python-dateutil

RUN mkdir /image_software
WORKDIR /image_software

# Install bedtools 2.26.0
RUN git clone --branch v2.26.0 https://github.com/arq5x/bedtools2.git
# RUN cd bedtools2 && make && cp -a /image_software/bedtools2/bin/. /usr/local/bin/
RUN cd bedtools2 && make && make install

# Install picard 1.92
RUN git clone --branch 1.92 https://github.com/broadinstitute/picard.git
RUN cd picard && ant -Ddist=/picard -lib lib/ant package-commands

# Install samtools dependencies
RUN wget http://zlib.net/zlib-1.2.11.tar.gz && tar -xvf zlib-1.2.11.tar.gz
RUN cd zlib-1.2.11 && ./configure && make && make install
RUN wget http://bzip.org/1.0.6/bzip2-1.0.6.tar.gz && tar -xvf bzip2-1.0.6.tar.gz
RUN cd bzip2-1.0.6 && make && make install
RUN wget https://tukaani.org/xz/xz-5.2.3.tar.gz && tar -xvf xz-5.2.3.tar.gz
RUN cd xz-5.2.3 && ./configure && make && make install
# Install samtools 1.0
RUN git clone --branch 1.5 https://github.com/samtools/samtools.git
RUN git clone --branch 1.5 git://github.com/samtools/htslib.git
RUN cd samtools && make && make install

# Set up the user directory
RUN groupadd -r encode && useradd --no-log-init -r -g encode encode
WORKDIR ~encode
# Get ENCODE pipeline container repository
ARG COMMIT=none
ARG BRANCH=fix_samtools_versions
RUN git clone --branch $BRANCH https://github.com/ENCODE-DCC/pipeline-container.git
RUN cd pipeline-container && git fetch && git pull

ENTRYPOINT ["python", "pipeline-container/src/filter_qc.py"]