import logging
import subprocess
import os
import asyncio
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load credentials securely from the .env file
load_dotenv()

# --- SECURE CONFIGURATION ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID_STR = os.getenv("TELEGRAM_ALLOWED_USER_ID", "0")
ALLOWED_USER_ID = int(ALLOWED_USER_ID_STR.strip('"').strip("'")) if ALLOWED_USER_ID_STR else 0
GEMINI_PATH = os.getenv("GEMINI_PATH", "gemini").strip('"').strip("'")
RULES_FILE = os.path.expanduser("~/.gemini_bot_rules.md")

if not BOT_TOKEN or ALLOWED_USER_ID == 0:
    print("❌ ERROR: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_ALLOWED_USER_ID in .env file.")
    exit(1)

# Global Session State
ACTIVE_SESSION = 'latest'
# ----------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def is_authorized(update: Update):
    if not update.effective_user:
        return False
    return update.effective_user.id == ALLOWED_USER_ID

async def setup_commands(application):
    commands = [
        BotCommand("chat", "Chat in current session"),
        BotCommand("sessions", "List all chat sessions"),
        BotCommand("switch", "Switch to a specific session number"),
        BotCommand("newchat", "Start a completely new session"),
        BotCommand("compact", "Summarize current session to save context"),
        BotCommand("sh", "Execute a shell command"),
        BotCommand("gemini", "Ask a stateless one-off question"),
        BotCommand("rules", "View persistent rules"),
        BotCommand("addrule", "Add a persistent rule")
    ]
    await application.bot.set_my_commands(commands)

def build_gemini_cmd(prompt, use_latest=False):
    global ACTIVE_SESSION
    if not os.path.exists(RULES_FILE):
        open(RULES_FILE, 'w').write("# Bot Rules\n")
    
    cmd_parts = [
        GEMINI_PATH,
        "--yolo",
        f"--policy {RULES_FILE}"
    ]
    
    if use_latest:
        cmd_parts.append(f"-r {ACTIVE_SESSION}")
    
    escaped_prompt = prompt.replace('"', '\\"')
    cmd_parts.append(f'-p "{escaped_prompt}"')
    return " ".join(cmd_parts)

async def execute_gemini(cmd_string):
    try:
        process = await asyncio.create_subprocess_shell(
            cmd_string,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy()
        )
        stdout, stderr = await process.communicate()
        output = (stdout.decode() + stderr.decode()).strip()
        lines = output.split('\n')
        clean_lines = [l for l in lines if "YOLO mode is enabled" not in l and l.strip() != ""]
        output = "\n".join(clean_lines)
        if not output: output = "[Gemini finished with no output]"
        return output
    except Exception as e:
        return f"❌ Error calling Gemini: {str(e)}"

async def list_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    await update.message.reply_chat_action("typing")
    cmd = f"{GEMINI_PATH} --list-sessions"
    output = await execute_gemini(cmd)
    active_str = f"**Currently Active Session:** `{ACTIVE_SESSION}`\n\n"
    await update.message.reply_text(active_str + output, parse_mode="Markdown")

async def switch_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    global ACTIVE_SESSION
    
    if not context.args:
        await update.message.reply_text("Usage: `/switch <session_number>` or `/switch latest`", parse_mode="Markdown")
        return
        
    target = context.args[0]
    if target == 'latest':
        ACTIVE_SESSION = 'latest'
        await update.message.reply_text("🔄 Switched active session to **latest**.", parse_mode="Markdown")
        return
        
    if not target.isdigit():
        await update.message.reply_text("❌ Please provide a valid session number from the `/sessions` list.")
        return
        
    ACTIVE_SESSION = target
    await update.message.reply_text(f"🔄 Switched active session to **#{ACTIVE_SESSION}**.\n\nType `/chat <message>` or send a direct message to continue.", parse_mode="Markdown")

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    global ACTIVE_SESSION
    prompt = "Hello! Let's start a new chat session."
    if context.args: prompt = " ".join(context.args)
    await update.message.reply_chat_action("typing")
    cmd_parts = [GEMINI_PATH, "--yolo", f"--policy {RULES_FILE}"]
    escaped_prompt = prompt.replace('"', '\\"')
    cmd_parts.append(f'-p "{escaped_prompt}"')
    
    res = await execute_gemini(" ".join(cmd_parts))
    ACTIVE_SESSION = 'latest'
    if len(res) > 4000: res = res[:4000] + "\n...[truncated]"
    await update.message.reply_text(f"🆕 **New Chat Started!**\n\n{res}", parse_mode="Markdown")

async def chat_stateful(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str = None):
    if not is_authorized(update): return
    if prompt is None: prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text(f"Usage: `/chat <message>`\n*(Targeting session: {ACTIVE_SESSION})*", parse_mode="Markdown")
        return
    await update.message.reply_chat_action("typing")
    res = await execute_gemini(build_gemini_cmd(prompt, use_latest=True))
    if len(res) > 4000: res = res[:4000] + "\n...[truncated]"
    await update.message.reply_text(res)

async def gemini_stateless(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Usage: `/gemini <prompt>`")
        return
    await update.message.reply_chat_action("typing")
    res = await execute_gemini(build_gemini_cmd(prompt, use_latest=False))
    if len(res) > 4000: res = res[:4000] + "\n...[truncated]"
    await update.message.reply_text(f"*{res}*", parse_mode="Markdown")

async def run_shell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    cmd = " ".join(context.args)
    if not cmd:
        await update.message.reply_text("Usage: `/sh <command>`", parse_mode="Markdown")
        return
    await update.message.reply_chat_action("typing")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        output = (result.stdout + result.stderr).strip()
        if not output: output = "[Success, no output]"
    except subprocess.TimeoutExpired:
        output = "❌ Command timed out (60s)"
    except Exception as e:
        output = f"❌ Error: {str(e)}"
    if len(output) > 4000: output = output[:4000] + "\n...[truncated]"
    await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")

async def compact_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    global ACTIVE_SESSION
    await update.message.reply_chat_action("typing")
    summary_prompt = "CRITICAL INSTRUCTION: Summarize our entire conversation history up to this point. Extract all key facts, established parameters, current task progress, and goals. Be concise but retain all technical details. Do NOT include filler text."
    summary = await execute_gemini(build_gemini_cmd(summary_prompt, use_latest=True))
    clean_summary = summary.replace('"', '\\"')
    inject_prompt = f"We are continuing a previous session (compacted). Here is the summary:\\n{clean_summary}\\n\\nAcknowledge this summary and await my next command."
    cmd_parts = [GEMINI_PATH, "--yolo", f"--policy {RULES_FILE}", f'-p "{inject_prompt}"']
    await execute_gemini(" ".join(cmd_parts))
    ACTIVE_SESSION = 'latest'
    await update.message.reply_text("🗜️ **Context Compacted!**\nA new session has been started containing your compressed history. Active session reset to `latest`.")

async def view_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    if not os.path.exists(RULES_FILE):
        await update.message.reply_text("No rules defined yet.")
        return
    with open(RULES_FILE, 'r') as f: content = f.read()
    await update.message.reply_text(f"📜 **Current Rules:**\n```\n{content}\n```", parse_mode="Markdown")

async def add_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    rule = " ".join(context.args)
    if not rule:
        await update.message.reply_text("Usage: `/addrule <rule text>`")
        return
    with open(RULES_FILE, 'a') as f: f.write(f"\n- {rule}")
    await update.message.reply_text("✅ Rule added persistently.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    await chat_stateful(update, context, update.message.text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('sh', run_shell))
    application.add_handler(CommandHandler('sessions', list_sessions))
    application.add_handler(CommandHandler('switch', switch_session))
    application.add_handler(CommandHandler('newchat', new_chat))
    application.add_handler(CommandHandler('gemini', gemini_stateless))
    application.add_handler(CommandHandler('chat', chat_stateful))
    application.add_handler(CommandHandler('compact', compact_context))
    application.add_handler(CommandHandler('rules', view_rules))
    application.add_handler(CommandHandler('addrule', add_rule))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    async def post_init(application): await setup_commands(application)
    application.post_init = post_init
    
    print("Bridge V3 (Multi-session) Open-Source initialized...")
    application.run_polling()
