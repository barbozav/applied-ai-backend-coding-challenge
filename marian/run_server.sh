#!/bin/sh
$PWD/marian-nmt/src/marian/build/marian-server --port 8080 \
    -m data/model.npz \
    -v data/corpus.en.yml data/corpus.es.yml
