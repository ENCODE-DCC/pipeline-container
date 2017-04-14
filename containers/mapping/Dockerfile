FROM ubuntu:14.04
RUN apt-get update && apt-get install -y wget unzip
RUN cd /tmp && wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.36.zip
RUN cd /tmp && unzip Trimmomatic-0.36.zip && cd Trimmomatic-0.36 && ls
RUN apt-get install -y git build-essential zlib1g-dev libncurses5-dev libncursesw5-dev python-dev python-setuptools openjdk-6-jdk
RUN cd /tmp && mkdir bwa_0_7_10
RUN cd /tmp/bwa_0_7_10 && git clone --branch 0.7.10 https://github.com/lh3/bwa.git
RUN cd /tmp/bwa_0_7_10/bwa && make
RUN cd /tmp && git clone https://github.com/ENCODE-DCC/pipeline-container.git && cd /tmp/pipeline-container && git checkout dissection-idan
RUN cd /tmp/pipeline-container && git fetch && git pull
RUN cd /tmp && mkdir reference_files
WORKDIR /tmp/pipeline-container
