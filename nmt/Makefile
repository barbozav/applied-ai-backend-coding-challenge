PWD       = $(shell pwd)

APP     := nmt-worker

SRC_DIR := $(PWD)/src
BIN_DIR := $(PWD)/bin
APP_DIR := $(SRC_DIR)/application

APP_SRCS := \
	$(SRC_DIR)/worker/translation.cpp \
	$(SRC_DIR)/worker/consumer.cpp \
	$(SRC_DIR)/main.cpp

INCLUDE  = -I$(SRC_DIR) -I/usr/local/include
LIBRARY  = -L. -L/usr/local/lib
CPPFLAGS = -Wall -O3

.PHONY: all install run clean

all: $(APP) install

$(APP): $(APP_SRCS)
	g++ $(INCLUDE) $(LIBRARY) $(CPPFLAGS) -o $@ $(APP_SRCS) -lSimpleAmqpClient -lcurl
install: $(APP)
	install -d $(BIN_DIR)
	mv $(APP) $(BIN_DIR)

run: install
	LD_LIBRARY_PATH=$(BIN_DIR):/usr/local/lib/x86_64-linux-gnu:/usr/local/lib $(BIN_DIR)/$(APP)

clean:
	rm $(BIN_DIR)/*
