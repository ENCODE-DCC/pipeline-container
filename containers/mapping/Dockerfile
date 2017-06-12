FROM ubuntu
RUN apt-get update && apt-get install -y wget unzip
RUN mkdir tmp1
RUN cd /tmp1 && wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.36.zip
RUN cd /tmp1 && unzip Trimmomatic-0.36.zip && cd Trimmomatic-0.36 && ls
RUN apt-get install -y --fix-missing git build-essential zlib1g-dev libncurses5-dev libncursesw5-dev python-dev python-setuptools openjdk-8-jdk
RUN cd /tmp1 && mkdir bwa_0_7_10
RUN cd /tmp1/bwa_0_7_10 && git clone --branch 0.7.10 https://github.com/lh3/bwa.git
RUN cd /tmp1/bwa_0_7_10/bwa && make
ARG CACHEBUST=3
RUN cd /tmp1 && git clone https://github.com/ENCODE-DCC/pipeline-container.git && cd /tmp1/pipeline-container && git checkout dissection-idan
RUN cd /tmp1/pipeline-container && git fetch && git pull
RUN cd /tmp1 && mkdir reference_files

#CMD [ "python", "/tmp1/pipeline-container/containers/mapping/src/encode_map.py" ]
#ENTRYPOINT ["python", "/tmp1/pipeline-container/containers/mapping/src/encode_map.py"]
ENTRYPOINT ["python"]
#CMD ls
#WORKDIR /tmp1/pipeline-container