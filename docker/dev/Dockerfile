FROM debian:buster
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz -O - | tar xz
WORKDIR /ta-lib
RUN ./configure --prefix=/usr && make && make install

VOLUME  /venv

WORKDIR /tradingkit

ENTRYPOINT ["docker/dev/docker-entrypoint.sh"]
CMD ["tk", "--help"]