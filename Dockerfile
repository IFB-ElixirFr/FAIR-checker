## TO BE UPDATED
FROM ubuntu:18.04

#MAINTAINER Thomas Rosnet

RUN apt-get update

RUN apt-get install -y git curl wget bzip2 vim lynx

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}

SHELL ["/bin/bash", "-c"]

RUN conda update -y conda

# Initialize conda in bash config files:
RUN conda init bash

COPY environment.yml ./
RUN conda env create -f environment.yml
RUN source activate fair-checker-webapp
RUN echo "source activate fair-checker-webapp" > ~/.bashrc
ENV PATH /opt/conda/envs/fair-checker-webapp/bin:$PATH

#RUN conda install flask rdflib pyopenssl -c conda-forge
#RUN pip install rdflib-jsonld
#RUN pip install Flask-SSLify

EXPOSE 5000

COPY app.py .
COPY templates templates
COPY static static
COPY metrics metrics
COPY launch.sh .

RUN chmod +x launch.sh

#ENTRYPOINT [ "sh", "./launch.sh" ]
#CMD [ "python3", "app.py"]
#CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "app:app"]

#ENTRYPOINT ["conda", "run", "-n", "fair-checker-webapp", "python3", "app.py"]
#ENTRYPOINT ["conda", "run", "-n", "fair-checker-webapp", "sh", "./launch.sh"]

CMD /bin/bash -c 'source activate fair-checker-webapp && sh ./launch.sh'
