"""A Telegram chatbot powered by Google Gemini (Google AI Studio).

Commands:
    /start  - greet the user and explain what the bot does
    /help   - list the commands
    /clear  - forget the conversation and start fresh

Any other text message is sent to Gemini, which replies using the recent
conversation as context. Run it with:

    python bot.py

Keys come from a .env file in this folder (see .env.example). Never paste
real keys into this file.
"""

import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from gemini_chat import GeminiChat

load_dotenv()

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Telegram messages can be at most 4096 characters. Long Gemini replies
# are split into chunks a little under that.
CHUNK_SIZE = 4000

WELCOME_TEXT = (
    "Hi! I'm a chatbot powered by Google Gemini.\n\n"
    "Ask me anything — explain a topic, draft a message, brainstorm ideas, "
    "practise English. I remember the last few messages of our chat, so "
    "follow-up questions work too.\n\n"
    "Type /help to see the commands, and /clear whenever you want a "
    "fresh start."
)

HELP_TEXT = (
    "Here's what I understand:\n\n"
    "/start — say hello and see this intro\n"
    "/help — this list\n"
    "/clear — forget our conversation and start over\n\n"
    "Everything else you type goes to Gemini and gets an answer. "
    "Go ahead, ask something."
)

ERROR_TEXT = (
    "Sorry, something went wrong while I was thinking. "
    "Please try again in a moment."
)


def split_text(text, size=CHUNK_SIZE):
    """Split a long reply into Telegram-sized chunks, breaking on
    newlines or spaces where possible instead of mid-word."""
    chunks = []
    while len(text) > size:
        cut = text.rfind("\n", 0, size)
        if cut < size // 2:
            cut = text.rfind(" ", 0, size)
        if cut < size // 2:
            cut = size
        chunks.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    if text:
        chunks.append(text)
    return chunks


def get_chat(context):
    """Return this user's GeminiChat, creating it on first use. Each user
    gets their own, so conversations never mix between people."""
    chat = context.user_data.get("gemini_chat")
    if chat is None:
        chat = GeminiChat()
        context.user_data["gemini_chat"] = chat
    return chat


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_chat(context).reset()
    await update.message.reply_text(
        "Done — I've forgotten our conversation. Fresh start. What's next?"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = (update.message.text or "").strip()
    if not user_text:
        return
    # Show "typing…" while Gemini thinks. It disappears on its own after
    # a few seconds or when the reply arrives.
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )
    try:
        reply = await get_chat(context).reply(user_text)
    except Exception:
        logger.exception("Gemini request failed")
        await update.message.reply_text(ERROR_TEXT)
        return
    for chunk in split_text(reply):
        await update.message.reply_text(chunk)


def build_application():
    """Build the Telegram application. Kept separate from main() so the
    wiring can be checked without starting the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN is not set. Copy .env.example to .env and "
            "paste the token BotFather gave you."
        )
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and "
            "paste your free key from Google AI Studio."
        )
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )
    return app


def main():
    app = build_application()
    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
