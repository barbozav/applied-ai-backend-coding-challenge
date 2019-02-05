#!/bin/sh
cd marian-nmt
mkdir build
cd build
cmake ..
make -j2
