
CUR_DIR = $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
BUILD_DIR = $(CUR_DIR)/build/
COMMON_DIR := $(wildcard $(CUR_DIR)/common)

all:ASGVulDetector

dependency:
	pip3 install -r requirements.txt

BASGVulDetector:
	@echo "ASGVulDetector"
	@echo ${CUR_DIR}
	@echo ${BUILD_DIR}"ASGVulDetector"
	@echo ${COMMON_DIR}

ASGVulDetector:
	@echo "ASGVulDetector"
	@echo ${CUR_DIR}
	@echo ${BUILD_DIR}"ASGVulDetector"
	@echo ${COMMON_DIR}

benchmark:
	@mkdir -p build/

clean:
	@rm -rf build > /dev/null 2>&1|| true

.PHONY: all benchmark check dependency clean banner-watcher

.DEFAULT: all