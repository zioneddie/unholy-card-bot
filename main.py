import re
import io
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Hardcoded Bot Token for Bot #2
BOT_TOKEN = "8880619234:AAFakyjGexW9iNsAcG1SujCj9ExTgnYIEVU"

def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines

def generate_confession_card(clean_text: str) -> io.BytesIO:
    width, height = 1080, 1080
    bg_color = (7, 8, 11)  # #07080B
    
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Card background dimensions
    card_margin_x = 80
    card_margin_y = 120
    card_width = width - (card_margin_x * 2)
    card_height = height - (card_margin_y * 2)

    # Draw Card (#10121A with Gold Border)
    card_shape = [card_margin_x, card_margin_y, card_margin_x + card_width, card_margin_y + card_height]
    draw.rounded_rectangle(card_shape, radius=32, fill=(16, 18, 26), outline=(212, 175, 55), width=2)

    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
        body_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 38)
        footer_font = ImageFont.truetype("DejaVuSans.ttf", 28)
    except IOError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # 1. Header Title
    title_text = "🕯️ UNHOLY CONFESSION"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_w) / 2, card_margin_y + 60), title_text, font=title_font, fill=(212, 175, 55))

    # 2. Confession Text
    max_text_width = card_width - 120
    wrapped_lines = wrap_text(f'"{clean_text}"', body_font, max_text_width, draw)

    line_height = 52
    total_text_height = len(wrapped_lines) * line_height
    start_y = card_margin_y + 180 + ((card_height - 320 - total_text_height) / 2)

    for line in wrapped_lines:
        line_bbox = draw.textbbox((0, 0), line, font=body_font)
        line_w = line_bbox[2] - line_bbox[0]
        draw.text(((width - line_w) / 2, start_y), line, font=body_font, fill=(240, 240, 240))
        start_y += line_height

    # 3. Footer Branding
    footer_text = "unholyconfessions.online  •  @UnholyPriet"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    footer_w = footer_bbox[2] - footer_bbox[0]
    draw.text(((width - footer_w) / 2, card_margin_y + card_height - 70), footer_text, font=footer_font, fill=(150, 150, 150))

    bio = io.BytesIO()
    bio.name = 'confession_card.png'
    image.save(bio, 'PNG')
    bio.seek(0)
    return bio

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    # Clean up copied message headers automatically
    clean_text = re.sub(r'<[^>]+>', '', text)
    clean_text = re.sub(r'🚨\s*NEW UNHOLY CONFESSION', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'Category:.*?\n', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'Severity:.*?\n', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'Confession:\s*', '', clean_text, flags=re.IGNORECASE)
    clean_text = clean_text.strip().strip('"')

    if not clean_text:
        await update.message.reply_text("Couldn't find any confession text in that message!")
        return

    card_buffer = generate_confession_card(clean_text)

    await update.message.reply_photo(
        photo=card_buffer,
        caption="✨ Here is your card! Ready to post on X."
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Card Generator Bot is listening...")
    app.run_polling()

if __name__ == "__main__":
    main()
  
