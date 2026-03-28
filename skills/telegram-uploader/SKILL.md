---
name: telegram-uploader
description: Sends images, files, or notifications to the user's Telegram chat using the bot API. Use this whenever the user needs to see a screenshot or a file privately.
---

# Telegram Uploader Skill

This skill allows you to send media and files directly to the user's Telegram chat via a bot. This is the preferred way to share visual results privately.

## Credentials
The bot token and user ID are stored in: `/home/ottopia/workspace/gemini-telegram-bot/.env`

## Usage Patterns

### Sending a Photo
To send an image from the workspace:
```bash
# First, extract variables (or just use them if already known)
TOKEN="YOUR_BOT_TOKEN_HERE"
CHAT_ID="YOUR_CHAT_ID_HERE"
curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendPhoto" \
     -F chat_id="$CHAT_ID" \
     -F photo="@/path/to/image.png" \
     -F caption="Your description here"
```

### Sending a Document
For non-image files (PDFs, logs, etc.):
```bash
curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendDocument" \
     -F chat_id="$CHAT_ID" \
     -F document="@/path/to/file.txt"
```

## Best Practices
- **Privacy:** Use this instead of public image uploaders.
- **Verification:** Always check the JSON response from `curl` to ensure `"ok": true`.
- **Formatting:** Captions support basic Markdown or HTML if specified.
