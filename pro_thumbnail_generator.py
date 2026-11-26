import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

THUMB_DIRS = [
    (Path(r"E:\videos\IShowSpeed_PRO_REELS\THUMBNAILS"), Path(r"E:\videos\gta6_clip_factory\media\thumbnails")),
    (Path(r"E:\videos\TECHNO_GAMERZ_PRO_REELS\THUMBNAILS"), Path(r"E:\videos\gta6_clip_factory\media\thumbnails")),
]

HOOK_TEXTS = {
    "Speed_Reel_001": ("10 YEARS", "FOR THIS?!", "#FFE600"),
    "Speed_Reel_002": ("CRASHED IN", "10 SECONDS!", "#FF2A85"),
    "Speed_Reel_003": ("SPEED CALLED", "LUCIA WHAT?!", "#00F0FF"),
    "Speed_Reel_004": ("CARTEL BANK", "HEIST GONE WRONG", "#FFE600"),
    "Speed_Reel_005": ("HE JUST", "REALIZED!!", "#FF2A85"),
    "Speed_Reel_006": ("HOW IS THIS", "ALLOWED?!", "#FFE600"),
    "Speed_Reel_007": ("7 HOURS IN...", "NEW GUNS!", "#00F0FF"),
    "Speed_Reel_008": ("HOW DID SHE", "SURVIVE?!", "#FFE600"),
    "Speed_Reel_009": ("JIMMY IN", "GTA 6?!", "#00E676"),
    "Speed_Reel_010": ("23 HOURS", "NO SLEEP!!", "#FF2A85"),
    "Pro_Techno_Reel_001": ("BOSS OF GTA", "IS BACK!", "#FFE600"),
    "Pro_Techno_Reel_004": ("INSANE STORM", "PHYSICS!", "#00F0FF"),
    "Pro_Techno_Reel_006": ("GTA 6 HAS", "INSTAGRAM?!", "#FF2A85"),
    "Pro_Techno_Reel_008": ("NPC IN HIS", "TRUCK BED!", "#FFE600"),
    "Pro_Techno_Reel_014": ("JUMPED OUT", "FULL SPEED!", "#FF2A85"),
    "Pro_Techno_Reel_016": ("HE SKIPPED", "THE SCENE!!", "#FFE600"),
}

FONT_PATH = r"C:\Windows\Fonts\impact.ttf"
if not Path(FONT_PATH).exists():
    FONT_PATH = r"C:\Windows\Fonts\arialbd.ttf"


def style_thumbnail(src_img: Path, out_img: Path, line1: str, line2: str, accent: str):
    im = Image.open(src_img).convert("RGB")
    w, h = im.size

    # Boost contrast & color slightly for mobile CTR pop
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Sharpness(im).enhance(1.2)

    # Clean top header cover so old banner text never bleeds through
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rectangle([0, 0, w, 200], fill=(8, 9, 15, 255))
    for y in range(200, 320):
        alpha = int(200 * (1 - (y - 200) / 120))
        odraw.line([(0, y), (w, y)], fill=(8, 9, 15, alpha))
    for y in range(h - 320, h):
        alpha = int(210 * ((y - (h - 320)) / 320))
        odraw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

    im = Image.alpha_composite(im.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(im)

    f1 = ImageFont.truetype(FONT_PATH, 78)
    f2 = ImageFont.truetype(FONT_PATH, 96)

    def draw_stroked_center(y_pos, text, font, fill_color):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (w - tw) // 2
        # Drop shadow
        draw.text((x + 5, y_pos + 6), text, font=font, fill=(0, 0, 0, 230))
        # Thick black stroke
        draw.text((x, y_pos), text, font=font, fill=fill_color, stroke_width=8, stroke_fill=(0, 0, 0))

    # Top Viral Hook Badge
    draw_stroked_center(22, line1, f1, "#FFFFFF")
    draw_stroked_center(102, line2, f2, accent)

    # Subtle corner "4K 60FPS" or "GTA VI" pill at bottom-right
    f_badge = ImageFont.truetype(FONT_PATH, 34)
    badge_txt = "GTA VI • 60FPS"
    bb = draw.textbbox((0, 0), badge_txt, font=f_badge)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    bx, by = w - bw - 44, h - bh - 56
    draw.rounded_rectangle([bx - 16, by - 10, bx + bw + 16, by + bh + 12], radius=12, fill=(10, 12, 20, 220), outline=accent, width=3)
    draw.text((bx, by - 2), badge_txt, font=f_badge, fill="#FFFFFF")

    out_img.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(out_img, quality=94)


def main():
    count = 0
    # Process Speed Reels
    speed_dir = Path(r"E:\videos\IShowSpeed_PRO_REELS\THUMBNAILS")
    factory_thumbs = Path(r"E:\videos\gta6_clip_factory\media\thumbnails")
    for idx in range(1, 11):
        name = f"Speed_Reel_{idx:03d}"
        src = speed_dir / f"Reel_{idx:03d}.jpg"
        if src.exists() and name in HOOK_TEXTS:
            l1, l2, acc = HOOK_TEXTS[name]
            style_thumbnail(src, speed_dir / f"Viral_Thumb_{name}.jpg", l1, l2, acc)
            style_thumbnail(src, factory_thumbs / f"{name}.jpg", l1, l2, acc)
            count += 1

    # Process Techno Reels
    techno_dir = Path(r"E:\videos\TECHNO_GAMERZ_PRO_REELS\THUMBNAILS")
    for name in ["Pro_Techno_Reel_001", "Pro_Techno_Reel_004", "Pro_Techno_Reel_006", "Pro_Techno_Reel_008", "Pro_Techno_Reel_014", "Pro_Techno_Reel_016"]:
        src = techno_dir / f"{name}.jpg"
        if src.exists() and name in HOOK_TEXTS:
            l1, l2, acc = HOOK_TEXTS[name]
            style_thumbnail(src, techno_dir / f"Viral_Thumb_{name}.jpg", l1, l2, acc)
            style_thumbnail(src, factory_thumbs / f"{name}.jpg", l1, l2, acc)
            count += 1

    print(f"Generated {count} Pro Viral Hook Thumbnails!")


if __name__ == "__main__":
    main()
