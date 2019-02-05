#!/bin/sh
$PWD/marian-nmt/src/marian/build/marian \
    --workspace 1000 \
    --dim-vocabs 50000 \
    --train-sets $PWD/data/corpus.en $PWD/data/corpus.es \
    --after-epochs 100 \
    --after-batches 10 \
    --disp-label-counts \
    --max-length 10 \
    --cpu-threads 1 \
    --mini-batch-fit \
    --learn-rate 0.001 \
    --model $PWD/data/model.npz \
    --early-stopping 10
