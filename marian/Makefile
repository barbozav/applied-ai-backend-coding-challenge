PWD      = $(shell pwd)

DATA_DIR := $(PWD)/data

.PHONY: all

all: amun marian

data:
	chmod a+x $(PWD)/get_data.sh
	$(PWD)/get_data.sh

amun:
	chmod a+x $(PWD)/build_amun.sh
	$(PWD)/build_amun.sh

marian:
	chmod a+x $(PWD)/build_marian.sh
	$(PWD)/build_marian.sh

train:
	chmod a+x $(PWD)/train_marian.sh
	$(PWD)/train_marian.sh

run:
	chmod a+x $(PWD)/run_server.sh
	$(PWD)/run_server.sh
