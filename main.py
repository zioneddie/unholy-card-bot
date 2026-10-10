import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont
import io
import re
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8880619234:AAFakyjGexW9iNsAcG1SujCj9ExTgnYIEVU")

def get_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()

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
    bg_color = (7, 8, 11)
    card_color = (16, 18, 26)
    gold = (212, 175, 55)
    soft_gold = (180, 150, 50)
    white = (245, 245, 245)
    muted = (160, 160, 160)

    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Main card
    margin = 55
    draw.rounded_rectangle(
        [margin, margin + 20, width - margin, height - margin - 20],
        radius=36,
        fill=card_color,
        outline=gold,
        width=4
    )

    # Inner subtle border
    draw.rounded_rectangle(
        [margin + 12, margin + 32, width - margin - 12, height - margin - 32],
        radius=28,
        outline=(40, 35, 20),
        width=1
    )

    # Title
    title_font = get_font(44, bold=True)
    title = "🕯️  UNHOLY CONFESSION"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_w) / 2, 125), title, font=title_font, fill=gold)

    # Gold line under title
    draw.line([(170, 195), (width - 170, 195)], fill=soft_gold, width=2)

    # Adaptive font size
    text_len = len(clean_text)
    if text_len < 120:
        body_size = 46
        line_height = 60
    elif text_len < 280:
        body_size = 38
        line_height = 50
    elif text_len < 450:
        body_size = 32
        line_height = 44
    else:
        body_size = 28
        line_height = 38

    body_font = get_font(body_size)
    max_text_width = 820

    display_text = f'"{clean_text}"'
    lines = wrap_text(display_text, body_font, max_text_width, draw)

    total_text_height = len(lines) * line_height
    available_top = 230
    available_bottom = 880
    available_height = available_bottom - available_top

    start_y = available_top + max(0, (available_height - total_text_height) // 2)

    for line in lines:
        if start_y > available_bottom - 15:
            break
        line_bbox = draw.textbbox((0, 0), line, font=body_font)
        line_w = line_bbox[2] - line_bbox[0]
        x = (width - line_w) / 2
        draw.text((x, start_y), line, font=body_font, fill=white)
        start_y += line_height

    # Footer
    footer_font = get_font(26)
    footer = "unholyconfessions.online  •  @UnholyPriet"
    footer_bbox = draw.textbbox((0, 0), footer, font=footer_font)
    footer_w = footer_bbox[2] - footer_bbox[0]
    draw.text(((width - footer_w) / 2, 945), footer, font=footer_font, fill=muted)

    bio = io.BytesIO()
    bio.name = 'confession_card.png'
    image.save(bio, 'PNG')
    bio.seek(0)
    return bio

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text

    if text.startswith('/start'):
        await update.message.reply_text("Father is listening. Send your confession.")
        return

    try:
        if "Confession:" in text:
            clean_text = text.split("Confession:")[-1]
        else:
            clean_text = text

        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        clean_text = clean_text.replace('—', '-').replace('–', '-')
        clean_text = clean_text.replace('“', '"').replace('”', '"')
        clean_text = clean_text.replace('‘', "'").replace('’', "'")
        clean_text = clean_text.strip().strip('"').strip()

        if not clean_text:
            await update.message.reply_text("Couldn't find a confession in that message.")
            return

        logging.info(f"Generating card | length: {len(clean_text)}")

        card = generate_confession_card(clean_text)
        await update.message.reply_photo(photo=card, caption="✨ Ready to post on X.")

    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        await update.message.reply_text(f"Error generating card: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Safe version to avoid line break issues
    handler = MessageHandler(filters.TEXT & (\~filters.COMMAND), handle_message)
    app.add_handler(handler)

    print("Card Generator Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
