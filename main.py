import logging
import os
import re
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token fixed so the bot will start
BOT_TOKEN = "8880619234:AAFakyjGexW9iNsAcG1SujCj9ExTgnYIEVU"

# Updated to the new Make.com webhook URL
MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL", "https://hook.eu1.make.com/wecfeq4nogp98h1r87lm85iq360qva2w")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: 
        return

    text = update.message.text

    if text.startswith('/start'):
        await update.message.reply_text("The Keeper is listening. Send your confession.")
        return

    try:
        # Clean up the text
        if "Confession:" in text:
            clean_text = text.split("Confession:")[1]
        else:
            clean_text = text
            
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        clean_text = clean_text.replace('—', '-').replace('–', '-').replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
        clean_text = clean_text.strip().strip('"').strip()

        if not clean_text:
            clean_text = text.strip()

        logging.info(f"Sending confession to Make.com for card generation...")
        
        # Send the text to Make.com
        async with aiohttp.ClientSession() as session:
            payload = {"confession": clean_text}
            async with session.post(MAKE_WEBHOOK_URL, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logging.error(f"Make.com error: {error_text}")
                    await update.message.reply_text("Failed to trigger card generation. Check Make.com.")
                else:
                    logging.info("Successfully sent to Make.com!")
                    # Make.com will send the image back to you, so we don't reply here.

    except Exception as e:
        logging.error(f"Error sending to Make: {e}", exc_info=True)
        await update.message.reply_text(f"Error: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
