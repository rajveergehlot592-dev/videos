import yt_dlp
import json
import re
import os

os.makedirs("techno_work", exist_ok=True)

ydl_opts = {
    'getcomments': True,
    'skip_download': True,
    'extractor_args': {'youtube': {'comment_sort': ['top'], 'max_comments': ['400', 'all', '250', '0']}}
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info('https://youtu.be/169ZzvPxvvM', download=False)

# Save 1080p60 H.264 URL (299) and audio URL (140)
v_fmt = next(f for f in info['formats'] if f.get('format_id') == '299')
a_fmt = next(f for f in info['formats'] if f.get('format_id') == '140')

with open("techno_work/stream_url_1080p.txt", "w") as f:
    f.write(v_fmt['url'])
with open("techno_work/stream_url_audio.txt", "w") as f:
    f.write(a_fmt['url'])

print("Saved 1080p60 URL (res:", v_fmt.get('resolution'), "fps:", v_fmt.get('fps'), ") and audio URL (140).")
print("Description:\n", info.get('description', '')[:800])

comments = info.get('comments', [])
print(f"\nTotal comments fetched: {len(comments)}")

with open("techno_work/top_comments.json", "w", encoding="utf-8") as f:
    json.dump([{'author': c.get('author'), 'text': c.get('text'), 'likes': c.get('like_count')} for c in comments], f, indent=2)

# Parse timestamps
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

lines.sort(key=lambda x: x[0], reverse=True)
print(f"\nTimestamp lines found: {len(lines)}")
print("\n--- TOP LIKED TIMESTAMP COMMENTS ---")
for likes, author, line in lines[:40]:
    print(f"[{likes} likes | {parse_time(line)}s | {author}]: {line[:140]}")
