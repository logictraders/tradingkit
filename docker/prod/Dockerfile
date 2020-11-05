FROM debian:buster
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    wget

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -O - | tar xz
WORKDIR /ta-lib
RUN ./configure --prefix=/usr && make && make install

VOLUME /root/.br

COPY . /tradingkit
WORKDIR /tradingkit
RUN pip3 install .

ENTRYPOINT ["tk"]
CMD ["--help"]