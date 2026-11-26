import subprocess
import os

with open("techno_work/stream_url_1080p.txt", "r") as f:
    url = f.read().strip()

os.makedirs("techno_work/previews", exist_ok=True)

# Key timestamps spanning the full 7439s video
timestamps = [
    ("01_intro_15s", 15),
    ("02_opener_820s", 820),
    ("03_heist_890s", 890),
    ("04_early_1698s", 1698),
    ("05_room_door_2503s", 2503),
    ("06_cap_2684s", 2684),
    ("07_wind_2950s", 2950),
    ("08_khujara_3302s", 3302),
    ("09_cutscene_pel_3711s", 3711),
    ("10_rent_4000s", 4000),
    ("11_manners_4365s", 4365),
    ("12_nanga_5096s", 5096),
    ("13_part_5160s", 5160),
    ("14_harami_5748s", 5748),
    ("15_swim_6512s", 6512),
    ("16_car_jump_6589s", 6589),
    ("17_chacha_6644s", 6644),
    ("18_mandy_6795s", 6795),
    ("19_blush_7056s", 7056),
    ("20_outro_7415s", 7415)
]

for name, t in timestamps:
    out = f"techno_work/previews/{name}.jpg"
    if not os.path.exists(out):
        cmd = ["ffmpeg", "-y", "-ss", str(t), "-i", url, "-vframes", "1", "-update", "1", out]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Captured {name} at {t}s")

print("Done capturing 1080p preview frames!")
