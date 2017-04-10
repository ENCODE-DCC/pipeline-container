FROM ubuntu:14.04
RUN apt-get update && apt-get install -y git build-essential zlib1g-dev libncurses5-dev libncursesw5-dev python-dev python-setuptools ant openjdk-7-jdk
RUN sudo easy_install pip
RUN pip install common
pip install python-dateutil
RUN cd /tmp && git clone --branch 0.1.19 https://github.com/samtools/samtools.git
RUN cd /tmp && git clone --branch 1.92 https://github.com/broadinstitute/picard.git
RUN cd /tmp && git clone --branch v2.26.0 https://github.com/arq5x/bedtools2.git
RUN cd /tmp/samtools && make && cp /tmp/samtools/samtools /usr/local/bin/samtools
RUN cd /tmp/bedtools2 && make && cp -a /tmp/bedtools2/bin/. /usr/local/bin/
RUN cd /tmp && git clone https://github.com/ENCODE-DCC/pipeline-container.git && cd /tmp/pipeline-container && git checkout dissection-idan
RUN cd /tmp/picard && ant -DJAVA_HOME=/usr/lib/jvm/java-6-openjdk-amd64/ -Ddist=/picard -lib lib/ant package-commands
RUN cd /tmp/pipeline-container && git fetch && git pull
WORKDIR /tmp/pipeline-container