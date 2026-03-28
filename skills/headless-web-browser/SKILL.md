---
name: headless-web-browser
description: Allows Gemini CLI to use Playwright to browse the web, interact with pages, and extract data. Use when the user asks to browse dynamic websites, perform web automation, or get data from sites like Skyscanner or Booking.
---

# Headless Web Browser Skill

This skill allows you (Gemini CLI) to automate web browsing using Python and Playwright. 
A dedicated Python virtual environment with Playwright installed is available for your use.

## Environment Location
The virtual environment is located at: `/home/ottopia/workspace/web-automation-skill/venv`

## How to Browse
Whenever you need to browse a website, interact with elements, or extract data, you should:

1. Write a temporary Python script (e.g., `/home/ottopia/workspace/web-automation-skill/temp_script.py`) using the `playwright` sync API.
2. Execute the script using the virtual environment's python: 
   `/home/ottopia/workspace/web-automation-skill/venv/bin/python /home/ottopia/workspace/web-automation-skill/temp_script.py`
3. Read the standard output of the script to get your results.

## Playwright Template
Here is a template you can use to write your scripts:

```python
from playwright.sync_api import sync_playwright
import json

def run():
    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=True)
        # Use a realistic User-Agent to help bypass basic bot protection
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Navigate to URL
        page.goto('https://example.com', wait_until='domcontentloaded')
        
        # Example: Extract text or elements
        # text = page.locator('body').inner_text()
        # print(text)
        
        browser.close()

if __name__ == '__main__':
    run()
```

## Best Practices
- **Anti-Bot Defenses:** Travel sites like Skyscanner and Booking often have strong anti-bot defenses (like Cloudflare). Use realistic User-Agents, handle exceptions gracefully, and avoid trying to solve CAPTCHAs programmatically.
- **Timeouts:** Wait for specific selectors (`page.wait_for_selector('.flight-price', timeout=10000)`) rather than arbitrary `time.sleep()`.
- **Output:** Parse the data before printing it to standard output. Do NOT print large raw HTML strings, as this will clutter the CLI's context window. Always print structured data (like JSON or plain text summaries).