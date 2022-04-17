FROM python:3.10-slim

ARG ELECTRUM_VER=4.2.1
ARG DOGECOIN_VER=1.14.5

RUN useradd -m -d /home/tontine -s /bin/bash tontine
RUN apt-get update && apt-get -y upgrade && apt-get install -y gpg

ADD "dogecoin-${DOGECOIN_VER}" /opt/dogecoin
ADD "electrum-${ELECTRUM_VER}" /opt/electrum
RUN ln -sv /opt/electrum/AppRun /usr/bin/electrum
ENV PATH="/opt/dogecoin/bin:${PATH}"

ADD scripts/bootstrap-doge /usr/bin

ARG VERSION
ADD dist/tontine-${VERSION}-py3-none-any.whl /tmp
RUN pip install "/tmp/tontine-${VERSION}-py3-none-any.whl"

USER tontine
