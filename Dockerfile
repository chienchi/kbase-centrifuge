FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# Here we install a python coverage tool and an
# https library that is out of date in the base image.
RUN pip install coverage &&\
    apt-get update && apt-get install -y build-essential zlib1g-dev gawk wget bioperl
RUN mkdir -p /kb/data
COPY ./data/ /kb/data/
# For centrifuge bin  and Krona tools
WORKDIR /kb/module
RUN \
    git clone https://github.com/infphilo/centrifuge.git && \
    cd centrifuge && make && \
    make install prefix=/kb/deployment && \
    cd ../ && \
    git clone https://github.com/marbl/Krona && \
    cd Krona/KronaTools && \
    ./install.pl --prefix /kb/deployment && \
    mkdir taxonomy && \
    ./updateTaxonomy.sh 

#    ./install.pl && \
#    mkdir taxonomy && \
#    ./updateAccessions.sh

# For centrifuge dbs (rest of db installation to ref data mount in entrypoint.sh init script)
RUN mkdir -p /data/centrifuge
# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
