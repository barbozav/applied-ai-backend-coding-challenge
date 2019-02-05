#!/bin/sh

install -d data/
cd data/
wget https://object.pouta.csc.fi/OPUS-News-Commentary/v11/mono/en.txt.gz
wget https://object.pouta.csc.fi/OPUS-News-Commentary/v11/mono/es.txt.gz
gzip -d en.txt.gz
gzip -d es.txt.gz
