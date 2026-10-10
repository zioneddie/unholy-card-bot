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
            width = len(test_line) * 12
            
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
        if "Confession:" in text:
            clean_text = text.split("Confession:")[1]
        else:
            clean_text = text
            
        # Clean up HTML tags and replace unsupported unicode symbols (like em-dashes) to prevent  boxes
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        clean_text = clean_text.replace('<b>', '').replace('</b>', '')
        clean_text = clean_text.replace('—', '-').replace('–', '-').replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
        clean_text = clean_text.strip().strip('"').strip()

        if not clean_text:
            clean_text = text.strip()

        logging.info(f"Processing text length: {len(clean_text)}")
        
        # Draw Dark/Gold Card Image (1080x1080)
        image = Image.new("RGB", (1080, 1080), (7, 8, 11))
        draw = ImageDraw.Draw(image)
        
        # Card outer border
        draw.rounded_rectangle([60, 80, 1020, 1000], radius=32, fill=(16, 18, 26), outline=(212, 175, 55), width=3)
        
        # ADAPTIVE FONT SIZING: Automatically shrinks font for long text so it never overflows
        text_len = len(clean_text)
        if text_len < 150:
            body_size, line_height = 42, 56
        elif text_len < 350:
            body_size, line_height = 34, 46
        else:
            body_size, line_height = 24, 34  # Compact mode for long essays

        try:
            title_font = ImageFont.load_default(size=34)
            body_font = ImageFont.load_default(size=body_size)
            footer_font = ImageFont.load_default(size=24)
        except TypeError:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # Draw Header Title
        draw.text((100, 130), "🕯️ UNHOLY CONFESSION", font=title_font, fill=(212, 175, 55))

        # Wrap body text nicely across max width (880px)
        lines = wrap_text(f'"{clean_text}"', body_font, 880, draw)
        
        total_text_height = len(lines) * line_height
        start_y = max(220, 540 - (total_text_height / 2))
        
        # Safety check if it's an extremely long text
        if start_y + total_text_height > 890:
            start_y = 210

        for line in lines:
            if start_y > 880:  # Prevent touching footer
                break
            draw.text((100, start_y), line, font=body_font, fill=(240, 240, 240))
            start_y += line_height

        # Draw Footer Branding fixed neatly at the bottom
        draw.text((100, 930), "unholyconfessions.online  •  @UnholyPriet", font=footer_font, fill=(150, 150, 150))

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
    
