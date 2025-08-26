#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import os

out_dir = os.path.join(os.getcwd(), 'static', 'images')
os.makedirs(out_dir, exist_ok=True)
tokens = ['usd', 'eur', 'jpy', 'gbp', 'inr', 'aud', 'cad', 'cny', 'brl', 'zar']

for code in tokens:
    img = Image.new('RGB', (200,200), color='#dddddd')
    draw = ImageDraw.Draw(img)
    text = code.upper()
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    w, h = draw.textsize(text, font=font)
    draw.text(((200-w)/2,(200-h)/2), text, fill='black', font=font)
    img.save(os.path.join(out_dir, f"{code}.png"))
ph = Image.new('RGB', (200,200), color='#cccccc')
d = ImageDraw.Draw(ph)
msg = "No Image"
fw, fh = d.textsize(msg, font=font)
d.text(((200-fw)/2,(200-fh)/2), msg, fill='black', font=font)
ph.save(os.path.join(out_dir, "placeholder.png"))

print("✔ Generated images for:", ", ".join(tokens))
