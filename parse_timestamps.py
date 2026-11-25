import json
import re

with open('top_comments.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

ts_pattern = re.compile(r'(\d{1,2}:)?\d{1,2}:\d{2}')

found = []
all_timestamps = []

for item in data:
    text = item.get('text', '')
    matches = ts_pattern.findall(text)
    if matches:
        found.append(item)
        for line in text.split('\n'):
            line = line.strip()
            if any(ch.isdigit() and ':' in line for ch in line):
                all_timestamps.append((item.get('likes', 0), item.get('author'), line))

print(f"Total comments with timestamps: {len(found)}")
print(f"Total timestamp lines: {len(all_timestamps)}")

# Sort by likes
all_timestamps.sort(key=lambda x: x[0] or 0, reverse=True)

print("\n--- TOP TIMESTAMP COMMENTS ---")
for likes, author, line in all_timestamps[:40]:
    print(f"[{likes} likes | {author}]: {line}")
