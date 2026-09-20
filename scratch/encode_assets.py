import os
import shutil
import base64

source_dir = r"C:\Users\user\.gemini\antigravity\brain\90875850-0e73-466d-8a8b-2e1bae45df3f"
target_dir = r"c:\Users\user\OneDrive\Documents\GitHub\universal ai resume analyzer\assets"

os.makedirs(target_dir, exist_ok=True)

files = {
    "bat_wing_left": "bat_wing_left_1788541311863.png",
    "bat_ai_emblem": "bat_ai_emblem_1788541335095.png",
    "hero_bat_bg": "hero_bat_bg_1788541360456.png"
}

encoded = {}

for key, fname in files.items():
    src_path = os.path.join(source_dir, fname)
    dst_path = os.path.join(target_dir, f"{key}.png")
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        with open(dst_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            encoded[key] = f"data:image/png;base64,{b64}"
        print(f"Copied and encoded: {key} ({len(b64)} chars)")

# Write src/intro_assets.py
intro_assets_path = r"c:\Users\user\OneDrive\Documents\GitHub\universal ai resume analyzer\src\intro_assets.py"
with open(intro_assets_path, "w", encoding="utf-8") as f:
    f.write("# Generated base64 visual assets for Superhero Batwing Intro & Dark AI Theme\n\n")
    f.write(f'BAT_WING_LEFT_B64 = "{encoded.get("bat_wing_left", "")}"\n\n')
    f.write(f'BAT_AI_EMBLEM_B64 = "{encoded.get("bat_ai_emblem", "")}"\n\n')
    f.write(f'HERO_BAT_BG_B64 = "{encoded.get("hero_bat_bg", "")}"\n')

print("Created src/intro_assets.py successfully!")
