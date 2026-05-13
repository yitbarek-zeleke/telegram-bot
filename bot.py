from flask import Flask
from threading import Thread
import os
import asyncio

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction

# ---------------- TOKEN ----------------
TOKEN = "YOUR_NEW_BOT_TOKEN"

# ---------------- FLASK SERVER ----------------
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

Thread(target=run_web).start()

# ---------------- MENU ----------------
menu = ReplyKeyboardMarkup(
    [["🔍 Check Link", "ℹ Help"]],
    resize_keyboard=True
)

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
🤖 CyberSafe AI Assistant

Welcome 👋

I can detect:
✔ Safe links
✔ Suspicious links
✔ Dangerous links

📌 Just send a link or use buttons below.
"""
    await update.message.reply_text(text, reply_markup=menu)

# ---------------- HELP ----------------
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
ℹ Help Guide

Send any link like:
https://example.com

I will check:
✔ Security (HTTPS)
✔ Suspicious words
✔ Fake domains

Stay safe online 🛡
"""
    await update.message.reply_text(text)

# ---------------- ANALYSIS ----------------
def analyze(url):
    url = url.lower()
    score = 100
    reasons = []
    risk_count = 0

    # HTTPS check
    if not url.startswith("https://"):
        score -= 30
        reasons.append("No HTTPS security")
        risk_count += 1

    # suspicious words
    keywords = [
        "login",
        "free",
        "verify",
        "bonus",
        "gift",
        "password",
        "bank",
        "account"
    ]

    for k in keywords:
        if k in url:
            score -= 10
            reasons.append(f"Suspicious word: {k}")
            risk_count += 1

    # fake domains
    if ".xyz" in url or ".tk" in url or ".top" in url:
        score -= 25
        reasons.append("Risky domain extension")
        risk_count += 2

    # FINAL RESULT
    if score >= 80 and risk_count == 0:
        status = "🟢 SAFE"
        desc = "This link looks clean and secure."

    elif score >= 50 or risk_count == 1:
        status = "🟡 SUSPICIOUS"
        desc = "This link may be risky. Check before opening."

    else:
        status = "🔴 DANGEROUS"
        desc = "This link is unsafe. Avoid clicking it."

    return status, score, reasons, desc

# ---------------- MESSAGE HANDLER ----------------
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # button actions
    if text == "ℹ help":
        await help_cmd(update, context)
        return

    if text == "🔍 check link":
        await update.message.reply_text("Send me a link 🔍")
        return

    # only links allowed
    if "http" not in text:
        await update.message.reply_text(
            "⚠ Please send a valid link (http or https)"
        )
        return

    # typing animation
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    await asyncio.sleep(1)

    status, score, reasons, desc = analyze(text)

    msg = f"""
🤖 {status}
📊 Score: {score}/100

💬 {desc}
"""

    if reasons:
        msg += "\n📌 Analysis:\n"
        for r in reasons:
            msg += f"- {r}\n"

    msg += "\n🔐 Stay safe online!"

    await update.message.reply_text(msg)

# ---------------- MAIN BOT ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("🤖 Bot is running...")
app.run_polling()
