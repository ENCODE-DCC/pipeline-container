############################################################
# Dockerfile to build the post-procssing after mapping with 
# BWA step in the ENCODE Mapping ChIP-seq pipeline container 
# image
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Idan Gabdank

# Update the repository sources list
# Install base packages: git, python
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    python-dev \
    python-setuptools

# Install pip and python packages: common and python-dateutils
RUN easy_install pip
RUN pip install common
RUN pip install python-dateutil


RUN mkdir image_software

# Install samtools 0.1.19 and 1.0
RUN cd /image_software && mkdir samtools_0_1_19 && cd samtools_0_1_19 && git clone --branch 0.1.19 https://github.com/samtools/samtools.git
RUN cd /image_software && mkdir samtools_1_0 && cd samtools_1_0 && git clone --branch 1.0 https://github.com/samtools/samtools.git
RUN cd /image_software/samtools_0_1_19/samtools/ && make
RUN cd /image_software/samtools_1_0 && git clone --branch 1.0 git://github.com/samtools/htslib.git
RUN cd /image_software/samtools_1_0/samtools/ && make

# Install BWA 0.7.10
RUN cd /image_software && mkdir bwa_0_7_10
RUN cd /image_software/bwa_0_7_10 && git clone --branch 0.7.10 https://github.com/lh3/bwa.git
RUN cd /image_software/bwa_0_7_10/bwa && make

# Get ENCODE pipeline container repository
RUN cd /image_software && git clone https://github.com/ENCODE-DCC/pipeline-container.git 
RUN cd /image_software/pipeline-container && git fetch && git pull

ENTRYPOINT ["python", "/image_software/pipeline-container/src/encode_post_map.py"]