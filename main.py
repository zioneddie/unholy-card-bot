import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont
import io
import sys

# Set up logging to display clearly in Railway logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Your exact Card Bot Token
BOT_TOKEN = "8880619234:AAFakyjGexW9iNsAcG1SujCj9ExTgnYIEVU"

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines, current_line = [], []
    for word in words:
        test_line = ' '.join(current_line + [word])
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
        except AttributeError:
            width = len(test_line) * 10
            
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line: lines.append(' '.join(current_line))
            current_line = [word]
    if current_line: lines.append(' '.join(current_line))
    return lines

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: 
        return

    text = update.message.text
    logging.info(f"Received message: {text}")

    if text.startswith('/start'):
        await update.message.reply_text("Father is listening. Send your confession.")
        return

    try:
        logging.info("Generating confession card image...")
        
        # Draw Dark/Gold Card Image
        image = Image.new("RGB", (1080, 1080), (7, 8, 11))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle([80, 120, 1000, 960], radius=32, fill=(16, 18, 26), outline=(212, 175, 55), width=2)
        
        try:
            body_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 38)
        except IOError:
            body_font = ImageFont.load_default()

        cleaned_text = text.strip().strip(chr(34))
        lines = wrap_text(f'"{cleaned_text}"', body_font, 840, draw)
        start_y = 540 - (len(lines) * 26)
        
        for line in lines:
            draw.text((140, start_y), line, font=body_font, fill=(240, 240, 240))
            start_y += 52

        bio = io.BytesIO()
        bio.name = 'card.png'
        image.save(bio, 'PNG')
        bio.seek(0)
        
        await update.message.reply_photo(photo=bio, caption="✨ Ready to post on X.")
        logging.info("Card sent successfully to Telegram!")

    except Exception as e:
        logging.error(f"Error generating card: {e}", exc_info=True)
        await update.message.reply_text(f"Error generating card: {str(e)}")

def main():
    logging.info("Initializing Card Generator Bot application...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    logging.info("Card Generator Bot is now polling for updates...")
    app.run_polling()

if __name__ == '__main__':
    main()
    
