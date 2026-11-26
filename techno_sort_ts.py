import json
import re
import os
import subprocess

with open("techno_work/top_comments.json", "r", encoding="utf-8") as f:
    comments = json.load(f)

lines = []
for item in comments:
    text = item.get('text', '')
    for line in text.split('\n'):
        line = line.strip()
        if re.search(r'\b\d{1,2}:\d{2}\b', line):
            lines.append((item.get('likes') or 0, item.get('author'), line))

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

lines.sort(key=lambda x: parse_time(x[2]))
for likes, author, line in lines:
    t = parse_time(line)
    if t <= 7450:
        print(f"[{t:4d}s | {author}]: {line[:120]}")
