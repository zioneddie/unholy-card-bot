import logging
from telegram import Update, InputMediaPhoto
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

def split_into_slides(text, max_chars=240, max_slides=4):
    """Splits long confessions into sequential paragraph chunks for TikTok slides."""
    words = text.split()
    slides = []
    current_chunk = []
    current_len = 0
    
    for word in words:
        if current_len + len(word) + 1 > max_chars and current_chunk:
            slides.append(" ".join(current_chunk))
            current_chunk = [word]
            current_len = len(word)
            if len(slides) >= max_slides - 1:
                # Pack remaining words into the final allowed slide
                pass
        else:
            current_chunk.append(word)
            current_len += len(word) + 1
            
    if current_chunk:
        slides.append(" ".join(current_chunk))
        
    # If it exceeded max_slides, merge the remainder into the last slide
    if len(slides) > max_slides:
        last_slide = " ".join(slides[max_slides-1:])
        slides = slides[:max_slides-1] + [last_slide]
        
    return slides

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
            
        # Clean tags and normalize punctuation
        clean_text = re.sub(r'<[^>]+>', '', clean_text)
        clean_text = clean_text.replace('<b>', '').replace('</b>', '')
        clean_text = clean_text.replace('—', '-').replace('–', '-').replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
        clean_text = clean_text.strip().strip('"').strip()

        if not clean_text:
            clean_text = text.strip()

        logging.info(f"Splitting confession of length {len(clean_text)} into TikTok slides...")
        
        # Get slide chunks (max 4 slides)
        slide_texts = split_into_slides(clean_text, max_chars=260, max_slides=4)
        total_slides = len(slide_texts)
        
        media_group = []
        bios = [] # Keep references alive in memory until sent

        gold_color = (235, 195, 80)

        for i, chunk in enumerate(slide_texts):
            image = Image.new("RGB", (1080, 1080), (10, 12, 18))
            draw = ImageDraw.Draw(image)
            
            # Draw thick gold border & card background
            draw.rounded_rectangle([45, 55, 1035, 1025], radius=36, fill=(18, 22, 32), outline=gold_color, width=6)
            
            try:
                title_font = ImageFont.load_default(size=36)
                body_font = ImageFont.load_default(size=40) # Large, bold, readable font
                footer_font = ImageFont.load_default(size=24)
            except TypeError:
                title_font = ImageFont.load_default()
                body_font = ImageFont.load_default()
                footer_font = ImageFont.load_default()

            # Header with slide indicator if multiple slides
            if total_slides > 1:
                header_text = f"🕯️ UNHOLY CONFESSION ({i+1}/{total_slides})"
            else:
                header_text = "🕯️ UNHOLY CONFESSION"
                
            draw.text((100, 120), header_text, font=title_font, fill=gold_color)

            # Wrap slide body text
            display_text = f'"{chunk}"' if i == 0 else f'"{chunk}'
            if i == total_slides - 1 and not display_text.endswith('"'):
                display_text += '"'
            elif i < total_slides - 1 and not display_text.endswith('"'):
                display_text += '..."'

            lines = wrap_text(display_text, body_font, 880, draw)
            
            line_height = 56
            total_text_height = len(lines) * line_height
            start_y = max(220, 540 - (total_text_height / 2))
            
            for line in lines:
                if start_y > 880:
                    break
                draw.text((100, start_y), line, font=body_font, fill=(245, 245, 245))
                start_y += line_height

            # Footer Branding
            draw.text((100, 940), "unholyconfessions.online  •  @UnholyPriet", font=footer_font, fill=(160, 160, 170))

            bio = io.BytesIO()
            bio.name = f'slide_{i+1}.png'
            image.save(bio, 'PNG')
            bio.seek(0)
            bios.append(bio)
            
            caption = "✨ Ready for TikTok Slideshow!" if i == 0 else None
            media_group.append(InputMediaPhoto(media=bio, caption=caption))

        # Send all slides together as a gorgeous photo album
        await update.message.reply_media_group(media=media_group)
        logging.info(f"Successfully sent {total_slides} slides to Telegram!")

    except Exception as e:
        logging.error(f"Error generating slides: {e}", exc_info=True)
        await update.message.reply_text(f"Error generating cards: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
                
