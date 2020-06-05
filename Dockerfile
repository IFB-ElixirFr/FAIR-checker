FROM ubuntu:16.04

MAINTAINER Alban Gaignard <alban.gaignard@univ-nantes.fr>

RUN apt-get update

RUN apt-get install -y git curl wget bzip2 vim lynx

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}

SHELL ["/bin/bash", "-c"]

RUN conda update -y conda

RUN conda create --name bise-ld-webapp
RUN source activate bise-ld-webapp
RUN conda install flask rdflib pymongo pyopenssl -c conda-forge
RUN pip install rdflib-jsonld
RUN pip install Flask-SSLify

COPY app.py .
COPY templates templates
COPY static static
COPY launch.sh .

ENTRYPOINT [ "./launch.sh" ]
