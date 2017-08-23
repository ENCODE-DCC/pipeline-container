############################################################
# Dockerfile to build the cross correlation step in the 
# ENCODE Mapping ChIP-seq pipeline container image
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
    r-base \
    r-base-dev \
    zlib1g-dev \
    unzip \
    wget

# Install pip and python packages: common and python-dateutils
RUN easy_install pip
RUN pip install common
RUN pip install python-dateutil

RUN mkdir /image_software
WORKDIR /image_software

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
ENV PHANTOMPEAKQUALTOOLS_HOME /image_software/phantompeakqualtools

# Get ENCODE pipeline container repository
# This COPY asumes the build context is the root of the pipeline-container repo
# and it gets whatever is checked out plus local modifications
RUN mkdir pipeline-container
COPY / pipeline-container

# Set up the user directory
RUN groupadd -r encode && useradd --no-log-init -r -m -d /home/encode/ -g encode encode
USER encode
WORKDIR /home/encode

ENTRYPOINT ["python", "/image_software/pipeline-container/src/xcor_only.py"]
