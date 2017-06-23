############################################################
# Dockerfile to build the cross correlation step in the 
# ENCODE Mapping ChIP-seq pipeline container image
# Based on Ubuntu 14.04
############################################################

# Set the base image to Ubuntu 14.04
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Idan Gabdank

# Update the repository sources list
# Install base packages: git, python, wget, unzip, R
RUN apt-get update && apt-get install -y \
    r-base \
    r-base-dev \
    r-bioc-rsamtools \
    git \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    python-dev \
    python-setuptools \
    libboost-dev \
    wget \
    unzip 

RUN su - -c "R -e \"install.packages('caTools', repos = 'http://cran.rstudio.com/')\""
RUN su - -c "R -e \"install.packages('snow', repos = 'http://cran.rstudio.com/')\""

# Install pip and python packages: common and python-dateutils
RUN easy_install pip
RUN pip install common
RUN pip install python-dateutil

RUN mkdir image_software

# Install samtools 0.1.19
RUN cd /image_software && mkdir samtools_0_1_19 && cd samtools_0_1_19 && git clone --branch 0.1.19 https://github.com/samtools/samtools.git
RUN cd /image_software/samtools_0_1_19/samtools/ && make

# Install bedtools 2.26.0
RUN cd /image_software && git clone --branch v2.26.0 https://github.com/arq5x/bedtools2.git
RUN cd /image_software/bedtools2 && make && cp -a /image_software/bedtools2/bin/. /usr/local/bin/

# Install SPP 1.14
RUN cd /image_software && mkdir spp && cd spp && wget https://github.com/hms-dbmi/spp/archive/1.14.tar.gz
RUN cd /image_software/spp && ls && R CMD INSTALL 1.14.tar.gz

# Get ENCODE pipeline container repository
RUN cd /image_software && git clone https://github.com/ENCODE-DCC/pipeline-container.git
RUN cd /image_software/pipeline-container && git fetch && git pull

ENTRYPOINT ["python", "/image_software/pipeline-container/src/xcor.py"]