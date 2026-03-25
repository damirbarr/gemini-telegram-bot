.PHONY: install start stop status logs uninstall

SERVICE_FILE = ~/.config/systemd/user/gemini-telegram.service
CURRENT_DIR = $(shell pwd)
PYTHON_BIN = $(shell which python3)
NODE_BIN_DIR = $(shell dirname $$(which node 2>/dev/null || echo ""))

install:
	@echo "Installing dependencies..."
	pip3 install -r requirements.txt
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your Telegram tokens before running 'make start'."; \
	fi
	@echo "Configuring systemd service..."
	@mkdir -p ~/.config/systemd/user/
	@sed -e "s|@WORKING_DIR@|$(CURRENT_DIR)|g" \
	     -e "s|@PYTHON_PATH@|$(PYTHON_BIN)|g" \
	     -e "s|@NODE_PATH@|$(NODE_BIN_DIR)|g" \
	     gemini-telegram.service.template > $(SERVICE_FILE)
	systemctl --user daemon-reload
	@echo ""
	@echo "================================================="
	@echo "Installation complete!"
	@echo "Next steps:"
	@echo "  1. Edit .env with your tokens (nano .env)"
	@echo "  2. Run 'make start' to launch the bot in the background."
	@echo "================================================="

start:
	systemctl --user enable gemini-telegram
	systemctl --user start gemini-telegram
	loginctl enable-linger $$USER
	@echo "Service started! You can check status with 'make status'"

stop:
	systemctl --user stop gemini-telegram
	@echo "Service stopped."

status:
	systemctl --user status gemini-telegram

logs:
	journalctl --user -u gemini-telegram -f

uninstall:
	systemctl --user stop gemini-telegram || true
	systemctl --user disable gemini-telegram || true
	rm -f $(SERVICE_FILE)
	systemctl --user daemon-reload
	@echo "Uninstalled systemd service."