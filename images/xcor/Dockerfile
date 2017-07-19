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
    build-essential \
    git \
    libboost-dev \
    libncurses5-dev \
    libncursesw5-dev \
    python-dev \
    python-setuptools \
    r-base \
    r-base-dev \
    r-bioc-rsamtools \
    zlib1g-dev \
    unzip \
    wget

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

# Install bedtools 2.26.0
RUN git clone --branch v2.26.0 https://github.com/arq5x/bedtools2.git
RUN cd bedtools2 && make && make install

# Install R packages and spp needed for phantompeakqualtools
RUN wget -O spp_1.14.tar.gz https://github.com/hms-dbmi/spp/archive/1.14.tar.gz 
RUN R -e "install.packages('bitops', repos='http://cran.us.r-project.org'); \
          install.packages('caTools', repos = 'http://cran.rstudio.com/'); \
          install.packages('snow', repos = 'http://cran.rstudio.com/'); \
          install.packages('snowfall', repos='http://cran.us.r-project.org'); \
          source('http://bioconductor.org/biocLite.R'); \
          biocLite('Rsamtools',suppressUpdates=TRUE); \
          install.packages('./spp_1.14.tar.gz')"

# Get phantompeakqualtools
RUN git clone --branch 1.0 https://github.com/kundajelab/phantompeakqualtools.git
ENV PHANTOMPEAKQUALTOOLS_HOME /image_software/phantompeakqualtools/

# Get ENCODE pipeline container repository
# ARG COMMIT=none
# ARG BRANCH=master
# RUN git clone --branch $BRANCH https://github.com/ENCODE-DCC/pipeline-container.git
RUN mkdir pipeline-container
COPY / pipeline-container

# Set up the user directory
RUN groupadd -r encode && useradd --no-log-init -r -m -d /home/encode/ -g encode encode
USER encode
WORKDIR /home/encode

ENTRYPOINT ["python", "/image_software/pipeline-container/src/xcor.py"]
