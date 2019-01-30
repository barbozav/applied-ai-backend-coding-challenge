PWD       = $(shell pwd)

APP     := nmt-worker
# LIB     := libunbabel.so

SRC_DIR := $(PWD)/src
BIN_DIR := $(PWD)/bin
APP_DIR := $(SRC_DIR)/application
#LIB_DIR := $(SRC_DIR)/unbabel

APP_SRCS := $(SRC_DIR)/main.cpp

# LIB_SRCS    := \
# 	$(LIB_DIR)/GenericHandler.cpp \
# 	$(LIB_DIR)/LuminosityHandler.cpp \
# 	$(LIB_DIR)/ProximityHandler.cpp \
# 	$(LIB_DIR)/TemperatureHandler.cpp \
# 	$(LIB_DIR)/Environment.cpp \
# 	$(LIB_DIR)/SensorHandler.cpp \
# 	$(LIB_DIR)/Publisher.cpp

INCLUDE  = -I$(SRC_DIR) -I/usr/local/include
LIBRARY  = -L. -L/usr/local/lib
CPPFLAGS = -Wall -O3
#LDFLAGS  = -shared

.PHONY: all install run clean

all: $(APP) install

#$(LIB): $(LIB_SRCS)
#	g++ -fPIC $(INCLUDE) $(LIBRARY) $(CPPFLAGS) $(LDFLAGS) -o $@ $^

$(APP): $(APP_SRCS)
	g++ $(INCLUDE) $(LIBRARY) $(CPPFLAGS) -o $@ $(APP_SRCS) -lSimpleAmqpClient -lcurl
install: $(APP)
	install -d $(BIN_DIR)
	mv $(APP) $(BIN_DIR)
	#mv $(LIB) $(BIN_DIR)

run: install
	LD_LIBRARY_PATH=$(BIN_DIR):/usr/local/lib/x86_64-linux-gnu:/usr/local/lib $(BIN_DIR)/$(APP)

clean:
	rm $(BIN_DIR)/*
