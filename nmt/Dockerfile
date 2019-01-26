FROM ubuntu:latest

RUN apt-get update && apt-get install -y git build-essential cmake libssl-dev libboost-all-dev libblas-dev

WORKDIR /app
# RUN git clone https://github.com/marian-nmt/marian.git
RUN git clone https://github.com/nlohmann/json.git
RUN git clone https://github.com/alanxz/rabbitmq-c.git
RUN git clone https://github.com/alanxz/SimpleAmqpClient.git

# WORKDIR /app/marian
# RUN mkdir build
# WORKDIR /app/marian/build
# RUN cmake ..
# RUN make -j


WORKDIR /app/json
RUN mkdir build
WORKDIR /app/json/build
RUN cmake ..
RUN make -j
RUN make install

WORKDIR /app/rabbitmq-c
RUN mkdir build
WORKDIR /app/rabbitmq-c/build
RUN cmake ..
RUN cmake --build ..
RUN make install

WORKDIR /app/SimpleAmqpClient
RUN mkdir build
WORKDIR /app/SimpleAmqpClient/build
RUN cmake ..
RUN cmake --build ..
RUN make install
