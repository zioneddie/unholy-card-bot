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
            width = len(test_line) * 14
            
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
            
        # Clean tags and normalize characters to prevent glitches
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        clean_text = clean_text.replace('<b>', '').replace('</b>', '')
        clean_text = clean_text.replace('—', '-').replace('–', '-').replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
        clean_text = clean_text.strip().strip('"').strip()

        if not clean_text:
            clean_text = text.strip()

        # NGL-Inspired High-Impact Canvas (1080x1080)
        image = Image.new("RGB", (1080, 1080), (10, 12, 18))
        draw = ImageDraw.Draw(image)
        
        # Thicker, commanding gold border with a richer inner card container
        gold_color = (235, 195, 80)
        draw.rounded_rectangle([45, 55, 1035, 1025], radius=36, fill=(18, 22, 32), outline=gold_color, width=6)
        
        # Dynamic Adaptive Sizing for maximum mobile legibility
        text_len = len(clean_text)
        if text_len < 120:
            body_size, line_height = 46, 62
        elif text_len < 300:
            body_size, line_height = 36, 50
        else:
            body_size, line_height = 26, 38  # Clean, readable scale for essays

        try:
            title_font = ImageFont.load_default(size=38)
            body_font = ImageFont.load_default(size=body_size)
            footer_font = ImageFont.load_default(size=24)
        except TypeError:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # Bold Header Title
        draw.text((100, 120), "🕯️ UNHOLY CONFESSION", font=title_font, fill=gold_color)

        # Wrap text across wider, comfortable margins (880px max width)
        lines = wrap_text(f'"{clean_text}"', body_font, 880, draw)
        
        total_text_height = len(lines) * line_height
        start_y = max(220, 540 - (total_text_height / 2))
        
        for line in lines:
            if start_y > 880:
                break
            draw.text((100, start_y), line, font=body_font, fill=(245, 245, 245))
            start_y += line_height

        # Clean Footer Branding
        draw.text((100, 940), "unholyconfessions.online  •  @UnholyPriet", font=footer_font, fill=(160, 160, 170))

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
    
