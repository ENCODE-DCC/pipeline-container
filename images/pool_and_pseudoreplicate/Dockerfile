

# Set the base image to Ubuntu 14.04
FROM ubuntu:14.04

# File Author / Maintainer
MAINTAINER Otto Jolanki

# Update the repository sources list
# Install base packages: git, python, wget, unzip, R
RUN apt-get update && apt-get install -y \
    git \
    python-dev \
    python-setuptools 

# Install pip and python packages: common and python-dateutils
RUN easy_install pip
RUN pip install common
RUN pip install python-dateutil
RUN pip install python-magic

RUN mkdir /image_software
WORKDIR /image_software

# Get ENCODE pipeline container repository
# This COPY asumes the build context is the root of the pipeline-container repo
# and it gets whatever is checked out plus local modifications
RUN mkdir pipeline-container
COPY / pipeline-container

# Set up the user directory
RUN groupadd -r encode && useradd --no-log-init -r -m -d /home/encode/ -g encode encode
USER encode
WORKDIR /home/encode

#ENTRYPOINT ["python", "/image_software/pipeline-container/src/encode_map.py"]
CMD ["bash"]
