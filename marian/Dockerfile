FROM ubuntu:latest

RUN mkdir /server
RUN mkdir /server/data
WORKDIR /server

COPY ./Makefile /server
COPY ./get_data.sh /server
COPY ./build_amun.sh /server
COPY ./build_marian.sh /server
COPY ./train_marian.sh /server
COPY ./run_server.sh /server
COPY ./data /server/data

RUN apt-get update && apt-get install -y git build-essential cmake libssl-dev libboost-all-dev libblas-dev google-perftools

RUN git clone https://github.com/marian-nmt/marian.git marian-nmt
WORKDIR /server/marian-nmt
RUN git fetch --all --tags
RUN git checkout 1.6.0
RUN git submodule update --init

WORKDIR /server
RUN make all

EXPOSE 8080
