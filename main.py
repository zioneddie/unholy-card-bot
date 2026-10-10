import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont
import io
import re

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
            width = len(test_line) * 18
            
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

    if text.startswith('/start'):
        await update.message.reply_text("Father is listening. Send your confession.")
        return

    try:
        # Foolproof extraction: take everything strictly after "Confession:" if it exists
        if "Confession:" in text:
            clean_text = text.split("Confession:")[1]
        else:
            clean_text = text
            
        # Clean up HTML tags, quotes, and extra whitespace
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        clean_text = clean_text.replace('<b>', '').replace('</b>', '').strip().strip('"').strip()

        if not clean_text:
            clean_text = text.strip()

        logging.info(f"Cleaned text for card: {clean_text}")
        
        # Draw Dark/Gold Card Image (1080x1080)
        image = Image.new("RGB", (1080, 1080), (7, 8, 11))
        draw = ImageDraw.Draw(image)
        
        # Card outer border
        draw.rounded_rectangle([60, 80, 1020, 1000], radius=32, fill=(16, 18, 26), outline=(212, 175, 55), width=3)
        
        # Use Pillow 11+ built-in scalable default font to guarantee large, readable text anywhere
        try:
            title_font = ImageFont.load_default(size=36)
            body_font = ImageFont.load_default(size=44)
            footer_font = ImageFont.load_default(size=26)
        except TypeError:
            # Fallback for older environments if needed
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # Draw Header Title
        draw.text((100, 140), "🕯️ UNHOLY CONFESSION", font=title_font, fill=(212, 175, 55))

        # Wrap body text nicely across the card width (880px max)
        lines = wrap_text(f'"{clean_text}"', body_font, 880, draw)
        
        line_height = 60
        total_text_height = len(lines) * line_height
        start_y = max(260, 540 - (total_text_height / 2))
        
        for line in lines:
            draw.text((100, start_y), line, font=body_font, fill=(240, 240, 240))
            start_y += line_height

        # Draw Footer Branding
        draw.text((100, 920), "unholyconfessions.online  •  @UnholyPriet", font=footer_font, fill=(150, 150, 150))

        bio = io.BytesIO()
        bio.name = 'card.png'
        image.save(bio, 'PNG')
        bio.seek(0)
        
        await update.message.reply_photo(photo=bio, caption="✨ Ready to post on X.")

    except Exception as e:
        logging.error(f"Error generating card: {e}", exc_info=True)
        await update.message.reply_text(f"Error generating card: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
        
