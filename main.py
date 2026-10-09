import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont
import io
import re

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8880619234:AAFakyjGexW9iNsAcG1SujCj9ExTgnYIEVU"

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines, current_line = [], []
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            current_line.append(word)
        else:
            if current_line: lines.append(' '.join(current_line))
            current_line = [word]
    if current_line: lines.append(' '.join(current_line))
    return lines

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text
    clean_text = re.sub(r'<[^>]+>', '', text).strip().strip('"')
    if not clean_text: return

    # Draw Image
    image = Image.new("RGB", (1080, 1080), (7, 8, 11))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([80, 120, 1000, 960], radius=32, fill=(16, 18, 26), outline=(212, 175, 55), width=2)
    
    try:
        body_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 38)
    except:
        body_font = ImageFont.load_default()

    lines = wrap_text(f'"{clean_text}"', body_font, 840, draw)
    start_y = 540 - (len(lines) * 26)
    for line in lines:
        draw.text((140, start_y), line, font=body_font, fill=(240, 240, 240))
        start_y += 52

    bio = io.BytesIO()
    bio.name = 'card.png'
    image.save(bio, 'PNG')
    bio.seek(0)
    
    await update.message.reply_photo(photo=bio, caption="✨ Ready to post on X.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
    
