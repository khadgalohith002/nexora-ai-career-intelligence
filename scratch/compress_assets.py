import os
import base64
from PIL import Image

assets_dir = r"c:\Users\user\OneDrive\Documents\GitHub\universal ai resume analyzer\assets"

files = {
    "bat_wing_left": ("bat_wing_left.png", 600),
    "bat_ai_emblem": ("bat_ai_emblem.png", 400),
    "hero_bat_bg": ("hero_bat_bg.png", 800)
}

encoded = {}

for key, (fname, max_dim) in files.items():
    img_path = os.path.join(assets_dir, fname)
    if os.path.exists(img_path):
        img = Image.open(img_path)
        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        
        # Save to compressed byte buffer
        compressed_path = os.path.join(assets_dir, f"{key}_opt.png")
        img.save(compressed_path, format="PNG", optimize=True)
        
        with open(compressed_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            encoded[key] = f"data:image/png;base64,{b64}"
        print(f"Compressed {key}: original -> {len(b64)} b64 chars")

intro_assets_path = r"c:\Users\user\OneDrive\Documents\GitHub\universal ai resume analyzer\src\intro_assets.py"
with open(intro_assets_path, "w", encoding="utf-8") as f:
    f.write("# Web-optimized base64 visual assets for Superhero Batwing Intro & Dark AI Theme\n\n")
    f.write(f'BAT_WING_LEFT_B64 = "{encoded.get("bat_wing_left", "")}"\n\n')
    f.write(f'BAT_AI_EMBLEM_B64 = "{encoded.get("bat_ai_emblem", "")}"\n\n')
    f.write(f'HERO_BAT_BG_B64 = "{encoded.get("hero_bat_bg", "")}"\n')

print("Updated src/intro_assets.py with web-optimized assets!")
