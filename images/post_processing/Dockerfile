############################################################
# Dockerfile to build the post-procssing after mapping with 
# BWA step in the ENCODE Mapping ChIP-seq pipeline container 
# image
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Idan Gabdank

# Update the repository sources list
# Install base packages: git, python
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libncurses5-dev \
    libncursesw5-dev \
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

# Install samtools dependencies
RUN wget http://zlib.net/zlib-1.2.11.tar.gz && tar -xvf zlib-1.2.11.tar.gz
RUN cd zlib-1.2.11 && ./configure && make && make install
RUN wget http://bzip.org/1.0.6/bzip2-1.0.6.tar.gz && tar -xvf bzip2-1.0.6.tar.gz
RUN cd bzip2-1.0.6 && make && make install
RUN wget https://tukaani.org/xz/xz-5.2.3.tar.gz && tar -xvf xz-5.2.3.tar.gz
RUN cd xz-5.2.3 && ./configure && make && make install
# Install samtools 1.5
RUN git clone --branch 1.5 https://github.com/samtools/samtools.git
RUN git clone --branch 1.5 git://github.com/samtools/htslib.git
RUN cd samtools && make && make install

# Install BWA 0.7.10
RUN git clone --branch 0.7.10 https://github.com/lh3/bwa.git
RUN cd bwa && make && cp bwa /usr/local/bin/

# Get ENCODE pipeline container repository
ARG COMMIT=none
ARG BRANCH=fix_samtools_versions
RUN git clone --branch $BRANCH https://github.com/ENCODE-DCC/pipeline-container.git

# Set up the user directory
RUN groupadd -r encode && useradd --no-log-init -r -m -d /home/encode/ -g encode encode
USER encode
WORKDIR /home/encode

ENTRYPOINT ["python", "/image_software/pipeline-container/src/encode_post_map.py"]
