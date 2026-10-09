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
            width = len(test_line) * 16
            
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
        # Clean up copied message headers and extract ONLY the actual confession text
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'🚨\s*NEW UNHOLY CONFESSION', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'Category:.*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'Severity:.*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'Confession:\s*', '', clean_text, flags=re.IGNORECASE)
        
        # Remove markdown bold/quotes remnants and extra spaces
        clean_text = clean_text.replace('<b>', '').replace('</b>', '').strip().strip('"')

        if not clean_text:
            clean_text = text.strip() # Fallback if regex clears too much

        logging.info(f"Cleaned confession text for card: {clean_text}")
        
        # Draw Dark/Gold Card Image (1080x1080)
        image = Image.new("RGB", (1080, 1080), (7, 8, 11))
        draw = ImageDraw.Draw(image)
        
        # Card outer border and background box
        draw.rounded_rectangle([60, 80, 1020, 1000], radius=32, fill=(16, 18, 26), outline=(212, 175, 55), width=3)
        
        try:
            title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
            body_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 48) # Larger, readable font
            footer_font = ImageFont.truetype("DejaVuSans.ttf", 28)
        except IOError:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # Draw Header Title
        draw.text((120, 140), "🕯️ UNHOLY CONFESSION", font=title_font, fill=(212, 175, 55))

        # Wrap confession body text (max width 840px)
        lines = wrap_text(f'"{clean_text}"', body_font, 840, draw)
        
        # Center text block vertically
        line_height = 64
        total_text_height = len(lines) * line_height
        start_y = max(260, 540 - (total_text_height / 2))
        
        for line in lines:
            draw.text((120, start_y), line, font=body_font, fill=(240, 240, 240))
            start_y += line_height

        # Draw Footer Branding
        draw.text((120, 920), "unholyconfessions.online  •  @UnholyPriet", font=footer_font, fill=(150, 150, 150))

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
    
