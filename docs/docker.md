# Creating a Docker image

This page describes how to create a custom docker image that runs an ipython
notebook server.


## Setup

- create a directory
- add the following files to the directory
  - `Dockerfile`, see below for contents
  - `Miniconda-latest-Linux-x86_64.sh`, download the latest
    Miniconda Python 2.7 Linux 64-bit installer from
    http://conda.pydata.org/miniconda.html
- run `docker build`, see docker's website for more details
  https://docs.docker.com/mac/step_four/


## Dockerfile
```
# Docker file to build geomag-algorithms ipython notebook container

FROM centos:6
MAINTAINER Jeremy Fee


# upgrade everything
RUN yum update -y
RUN yum install -y bzip2 git tar

# install miniconda
ADD Miniconda-latest-Linux-x86_64.sh /tmp/Miniconda-latest-Linux-x86_64.sh
RUN bash /tmp/Miniconda-latest-Linux-x86_64.sh -b

# install obspy, ipython notebook
RUN /root/miniconda/bin/conda install -c obspy obspy

# install geomag-algorithms
RUN /root/miniconda/bin/pip install git+https://github.com/usgs/geomag-algorithms.git

# install ipython notebook
RUN /root/miniconda/bin/conda install ipython-notebook


# run ipython notebook
RUN mkdir /var/notebooks
WORKDIR /var/notebooks
EXPOSE 8888
CMD /root/miniconda/bin/ipython notebook --ip=* --port=8888 --no-browser
```
