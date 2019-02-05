#!/bin/sh
cd marian-nmt/src/marian
mkdir build
cd build
cmake .. -DCOMPILE_CUDA=off
make -j2
