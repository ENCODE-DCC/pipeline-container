FROM ubuntu:14.04
RUN apt-get update && apt-get install -y git build-essential zlib1g-dev libncurses5-dev libncursesw5-dev python-dev python-setuptools
RUN sudo easy_install pip
RUN pip install common
RUN pip install python-dateutil

RUN cd /tmp && mkdir samtools_0_1_19 && cd samtools_0_1_19 && git clone --branch 0.1.19 https://github.com/samtools/samtools.git
RUN cd /tmp && mkdir samtools_1_0 && cd samtools_1_0 && git clone --branch 1.0 https://github.com/samtools/samtools.git
RUN cd /tmp/samtools_0_1_19/samtools/ && make
RUN cd /tmp/samtools_1_0 && git clone --branch 1.0 git://github.com/samtools/htslib.git
RUN cd /tmp/samtools_1_0/samtools/ && make


RUN cd /tmp && mkdir bwa_0_7_10
RUN cd /tmp/bwa_0_7_10 && git clone --branch 0.7.10 https://github.com/lh3/bwa.git
RUN cd /tmp/bwa_0_7_10/bwa && make

RUN cd /tmp && git clone https://github.com/ENCODE-DCC/pipeline-container.git && cd /tmp/pipeline-container && git checkout dissection-idan
RUN cd /tmp/pipeline-container && git fetch && git pull

RUN cd /tmp && mkdir reference_files

WORKDIR /tmp/pipeline-container

#RUN cd /tmp && git clone --branch v2.26.0 https://github.com/arq5x/bedtools2.git
#RUN cd /tmp/bedtools2 && make && cp -a /tmp/bedtools2/bin/. /usr/local/bin/