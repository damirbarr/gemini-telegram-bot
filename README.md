# Gemini Telegram Bridge 🚀

Turn any Linux machine into a fully autonomous, remote-controlled assistant via Telegram using the [Gemini CLI](https://geminicli.com/).

This bridge creates a highly secure, private connection between your personal Telegram account and your machine. It features persistent chat memory, context compaction, multi-chat management, and direct shell access.

## Features
- **Highly Secure:** Hardcoded to ONLY respond to your specific Telegram User ID. Ignores all other users completely.
- **Zero Downtime Updates:** Runs as a persistent `systemd` background service that auto-restarts.
- **Stateful Memory:** Remembers your conversation using Gemini CLI sessions.
- **Multi-Chat Management:** Seamlessly swap between multiple parallel tasks (`/sessions`, `/switch`, `/newchat`).
- **Context Compaction (`/compact`):** When chats get long and expensive, the bot autonomously reads the whole history, summarizes it down to key facts/goals, and injects it into a fresh session to save tokens.
- **Persistent Rules:** Use `/addrule` to add global instructions (like "Always write python 3.10" or "Be sarcastic") which persist across all chats.

## Setup Instructions

### Prerequisites
1. You must have [Python 3](https://python.org) and `pip3` installed.
2. You must have the [Gemini CLI](https://geminicli.com/) installed and authenticated (`gemini` command must work in your terminal).

### 1. Get Your Telegram Credentials
1. **Bot Token:** Open Telegram, message [@BotFather](https://t.me/BotFather), type `/newbot`, and follow the steps to get your API Token (e.g., `1234567890:ABCdef...`).
2. **User ID:** Open Telegram, message [@userinfobot](https://t.me/userinfobot), type `/start`, and copy your numerical `Id` (e.g., `123456789`). This guarantees *only you* can use the bot.

### 2. Installation
Clone this repository to your machine:
```bash
git clone https://github.com/damirbarr/gemini-telegram-bot.git
cd gemini-telegram-bot
```

Run the automated installer:
```bash
make install
```
*This will install Python dependencies and generate the systemd background service.*

### 3. Configuration
The installer created a `.env` file for you. Open it:
```bash
nano .env
```
Paste your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USER_ID`. If your `gemini` executable is not in the default path, update `GEMINI_PATH`.

### 4. Start the Bot
Start the background service so the bot runs forever, even when you log out:
```bash
make start
```

### Useful Makefile Commands
- `make start` - Starts the background service
- `make stop` - Stops the service
- `make status` - Check if the bot is running
- `make logs` - View the live terminal logs of the bot
- `make uninstall` - Completely removes the background service

## How to use the Bot
Open Telegram and message your bot!
- `/chat <msg>` - Talk to Gemini (stateful). Standard text messages also do this.
- `/sh <cmd>` - Run bash commands on your host machine.
- `/sessions` - View all active chat histories.
- `/switch <id>` - Jump between different tasks/chats.
- `/compact` - Compress your current chat history to save tokens.
- `/addrule <rule>` - Tell your agent how to behave globally.

---
*Created dynamically by the Gemini CLI.*