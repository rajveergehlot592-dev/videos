import json
import re
import os
import subprocess

with open("live3_work/top_comments.json", "r", encoding="utf-8") as f:
    comments = json.load(f)

def parse_time(s):
    m = re.search(r'(\d+):(\d{2})(?::(\d{2}))?', s)
    if not m:
        return 999999
    parts = [p for p in m.groups() if p is not None]
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 999999

lines = []
for item in comments:
    for line in item.get("text", "").split("\n"):
        line = line.strip()
        if re.search(r'\b\d{1,2}:\d{2}\b', line):
            t = parse_time(line)
            if t <= 85282:
                lines.append((t, item.get("author"), line))

lines.sort(key=lambda x: x[0])
print("--- TIMESTAMPS > 14650s ---")
for t, author, line in lines:
    if t > 14650:
        print(f"[{t:5d}s | {author}]: {line[:120]}")

with open("live3_work/stream_url_1080p.txt", "r") as f:
    url = f.read().strip()

os.makedirs("live3_work/previews", exist_ok=True)
samples = [
    ("01_24s", 24),
    ("02_861s", 861),
    ("03_1542s", 1542),
    ("04_4757s", 4757),
    ("05_5340s", 5340),
    ("06_5550s", 5550),
    ("07_6132s", 6132),
    ("08_7820s", 7820),
    ("09_9775s", 9775),
    ("10_9905s", 9905),
    ("11_14640s", 14640),
    ("12_25000s", 25000),
    ("13_45000s", 45000),
    ("14_65000s", 65000),
]

for name, t in samples:
    out = f"live3_work/previews/{name}.jpg"
    if not os.path.exists(out):
        subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", url, "-vframes", "1", "-update", "1", out],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Captured {name} at {t}s")
print("Done!")
