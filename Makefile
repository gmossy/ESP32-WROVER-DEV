# Makefile for ESP32-WROVER-DEV Camera Project
# Built by Glenn Mossy

# Configuration
BOARD_FQBN = esp32:esp32:esp32wrover
PORT ?= /dev/cu.usbserial-143130
UPLOAD_SPEED = 115200
SKETCH_DIR = camera_webserver

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help setup config compile upload monitor test docker clean all

# Default target
all: config compile upload

help:
	@echo "$(GREEN)ESP32-WROVER-DEV Camera Project - Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  make setup       - Initial setup (install dependencies)"
	@echo "  make config      - Generate config.h from .env"
	@echo "  make compile     - Compile the sketch"
	@echo "  make upload      - Upload to ESP32"
	@echo "  make monitor     - Open serial monitor"
	@echo "  make test        - Run connectivity tests"
	@echo "  make docker      - Start Docker services"
	@echo "  make docker-stop - Stop Docker services"
	@echo "  make clean       - Clean build files"
	@echo "  make all         - Config + Compile + Upload"
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make all PORT=/dev/cu.usbserial-143130"
	@echo "  make upload SKETCH_DIR=low_power_webserver"
	@echo ""

setup:
	@echo "$(GREEN)Setting up project...$(NC)"
	@echo "Checking for arduino-cli..."
	@command -v arduino-cli >/dev/null 2>&1 || { echo "$(RED)arduino-cli not found. Install with: brew install arduino-cli$(NC)"; exit 1; }
	@echo "Checking for Python 3..."
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)python3 not found$(NC)"; exit 1; }
	@echo "Checking for Docker..."
	@command -v docker >/dev/null 2>&1 || { echo "$(YELLOW)Docker not found (optional)$(NC)"; }
	@echo "$(GREEN)Checking ESP32 core...$(NC)"
	@arduino-cli core list | grep esp32:esp32 || arduino-cli core install esp32:esp32
	@echo "$(GREEN)Setup complete!$(NC)"

config:
	@echo "$(GREEN)Generating configuration from .env...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)No .env file found. Creating from template...$(NC)"; \
		cp .env.example .env; \
		echo "$(RED)Please edit .env with your WiFi credentials!$(NC)"; \
		exit 1; \
	fi
	@python3 generate_config.py
	@echo "$(GREEN)Configuration generated!$(NC)"

compile: config
	@echo "$(GREEN)Compiling $(SKETCH_DIR)...$(NC)"
	@cd $(SKETCH_DIR) && arduino-cli compile --fqbn $(BOARD_FQBN) .
	@echo "$(GREEN)Compilation successful!$(NC)"

upload: compile
	@echo "$(GREEN)Uploading to ESP32 on $(PORT)...$(NC)"
	@cd $(SKETCH_DIR) && arduino-cli upload --fqbn $(BOARD_FQBN) --port $(PORT) --upload-property upload.speed=$(UPLOAD_SPEED) .
	@echo "$(GREEN)Upload complete!$(NC)"

monitor:
	@echo "$(GREEN)Opening serial monitor on $(PORT)...$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to exit$(NC)"
	@arduino-cli monitor -p $(PORT) -c baudrate=115200

test:
	@echo "$(GREEN)Running connectivity tests...$(NC)"
	@python3 test.py

viewer:
	@echo "$(GREEN)Starting image viewer...$(NC)"
	@python3 view_captures.py

docker:
	@echo "$(GREEN)Starting Docker services...$(NC)"
	@cd n8n && docker-compose up -d
	@echo "$(GREEN)Docker services started!$(NC)"
	@echo "n8n:          http://localhost:5678"
	@echo "Image Viewer: http://localhost:8080"
	@echo "See n8n/README.md for details"

docker-stop:
	@echo "$(YELLOW)Stopping Docker services...$(NC)"
	@cd n8n && docker-compose down
	@echo "$(GREEN)Docker services stopped$(NC)"

docker-logs:
	@cd n8n && docker-compose logs -f

docker-rebuild:
	@echo "$(GREEN)Rebuilding Docker containers...$(NC)"
	@cd n8n && docker-compose down
	@cd n8n && docker-compose build --no-cache
	@cd n8n && docker-compose up -d

clean:
	@echo "$(YELLOW)Cleaning build files...$(NC)"
	@find . -name "*.elf" -delete
	@find . -name "*.bin" -delete
	@find . -name "*.hex" -delete
	@find . -name "build" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Clean complete!$(NC)"

clean-all: clean
	@echo "$(YELLOW)Cleaning config files...$(NC)"
	@find . -name "config.h" -delete
	@echo "$(GREEN)All clean!$(NC)"

# Quick shortcuts
c: compile
u: upload
m: monitor
t: test
d: docker

# Board detection
detect:
	@echo "$(GREEN)Detecting connected boards...$(NC)"
	@arduino-cli board list

# List available sketches
sketches:
	@echo "$(GREEN)Available sketches:$(NC)"
	@find . -name "*.ino" -type f | sed 's|^\./||' | grep -v "build/"

# Check environment
check:
	@echo "$(GREEN)Environment Check:$(NC)"
	@echo -n "arduino-cli: "
	@command -v arduino-cli >/dev/null 2>&1 && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"
	@echo -n "python3:     "
	@command -v python3 >/dev/null 2>&1 && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"
	@echo -n "docker:      "
	@command -v docker >/dev/null 2>&1 && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"
	@echo -n ".env file:   "
	@[ -f .env ] && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"
	@echo -n "config.h:    "
	@[ -f $(SKETCH_DIR)/config.h ] && echo "$(GREEN)✓$(NC)" || echo "$(RED)✗$(NC)"

# Development workflow
dev: config compile upload monitor

# Production build
prod: clean config compile upload test

# Install Python dependencies
install-deps:
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	@pip3 install requests

# Git operations
git-status:
	@git status

git-push: 
	@echo "$(GREEN)Committing and pushing changes...$(NC)"
	@git add -A
	@git status
	@echo "$(YELLOW)Enter commit message:$(NC)"
	@read -p "Message: " msg; git commit -m "$$msg"
	@git push

# Version info
version:
	@echo "$(GREEN)ESP32-WROVER-DEV Camera Project$(NC)"
	@echo "Built by Glenn Mossy"
	@echo ""
	@echo "arduino-cli version:"
	@arduino-cli version
	@echo ""
	@echo "ESP32 core version:"
	@arduino-cli core list | grep esp32:esp32

# Quick build for different sketches
camera: SKETCH_DIR=camera_webserver
camera: all

lowpower: SKETCH_DIR=low_power_webserver
lowpower: all

simple: SKETCH_DIR=simple
simple: all

webserver: SKETCH_DIR=webserver
webserver: all
