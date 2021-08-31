## TO BE UPDATED
FROM ubuntu:18.04

#MAINTAINER Thomas Rosnet

# create directory for the app user
RUN mkdir -p /home/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN apt-get update

RUN apt-get install -y git curl wget bzip2 vim lynx
#RUN apt-get install -y mongodb
RUN apt-get install -y gnupg2 unzip
RUN apt-get update -y
RUN apt-get install -y xvfb

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# Updating apt to see and install Google Chrome
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# Install miniconda to /miniconda
RUN curl -LO http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}


RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip

RUN CHROME_SETUP=google-chrome.deb && \
    wget -O $CHROME_SETUP "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" && \
    dpkg -i $CHROME_SETUP && \
    apt-get install -y -f && \
    rm $CHROME_SETUP

# # Install Chrome
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# RUN apt-get -y update
# RUN apt-get install -y google-chrome-stable
#
# # Install schrome-webdriver
# RUN apt-get install -yqq unzip
# RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
# RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
RUN xvfb :99 &
ENV DISPLAY=:99

SHELL ["/bin/bash", "-c"]

RUN conda update -y conda

# Initialize conda in bash config files:
RUN conda init bash

COPY environment.yml ./
RUN conda env create -f environment.yml

RUN source activate fair-checker-webapp
SHELL ["conda", "run", "-n", "fair-checker-webapp", "/bin/bash", "-c"]

# Demonstrate the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

RUN echo "source activate fair-checker-webapp" > ~/.bashrc
ENV PATH /opt/conda/envs/fair-checker-webapp/bin:$PATH

ARG FLASK_ENV
ENV FLASK_ENV ${FLASK_ENV}

#RUN conda install flask rdflib pyopenssl -c conda-forge
#RUN pip install rdflib-jsonld
#RUN pip install Flask-SSLify

EXPOSE 5000

COPY app.py .
COPY templates templates
COPY static static
COPY metrics metrics
COPY .env .
COPY launch_dev.sh .
COPY config.py .


RUN chmod +x launch_dev.sh

#ENTRYPOINT [ "sh", "./launch_dev.sh" ]
#CMD [ "python3", "app.py"]
#CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "app:app"]

#ENTRYPOINT ["conda", "run", "-n", "fair-checker-webapp", "python3", "app.py"]
#ENTRYPOINT ["conda", "run", "-n", "fair-checker-webapp", "sh", "./launch_dev.sh"]

# CMD /bin/bash -c 'conda run -n fair-checker-webapp && sh ./launch_dev.sh'
CMD /bin/bash -c 'source activate fair-checker-webapp && sh ./launch_dev.sh'
