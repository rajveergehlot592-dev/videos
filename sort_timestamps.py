import json
import re

with open('top_comments.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Collect all comments
lines = []
for item in data:
    text = item.get('text', '')
    for line in text.split('\n'):
        line = line.strip()
        if re.search(r'\b\d{1,2}:\d{2}\b', line):
            lines.append((item.get('likes', 0), item.get('author'), line))

print(f"Total timestamp lines: {len(lines)}")
# Print chronologically by parsing first timestamp
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

print("\n--- CHRONOLOGICAL HIGHLIGHTS FROM COMMUNITY ---")
for likes, author, line in lines:
    print(f"[{parse_time(line)}s | {likes} likes | {author}]: {line}")
