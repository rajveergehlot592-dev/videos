import yt_dlp
import json
import re
import os

os.makedirs("live3_work", exist_ok=True)

ydl_opts = {
    'getcomments': True,
    'skip_download': True,
    'extractor_args': {'youtube': {'comment_sort': ['top'], 'max_comments': ['400', 'all', '250', '0']}}
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info('https://www.youtube.com/live/hwSg39yIBGU', download=False)

print("Title:", info.get("title"))
print("Uploader:", info.get("uploader"))
print("Duration:", info.get("duration"), "s")

# List >=720p https formats
print("\n--- VIDEO FORMATS (>=720p) ---")
for f in info['formats']:
    if f.get('height') and f.get('height') >= 720 and f.get('vcodec') != 'none' and f.get('protocol') == 'https':
        print(f['format_id'], f.get('ext'), f.get('resolution'), f.get('fps'), f.get('vcodec'), f.get('tbr'))

# Pick best 1080p60 H.264 or best 1080p
v_fmt = next((f for f in info['formats'] if f.get('format_id') == '299'), None)
if not v_fmt:
    v_fmt = next((f for f in info['formats'] if f.get('height') and f.get('height') >= 1070 and 'avc1' in (f.get('vcodec') or '') and f.get('protocol') == 'https'), None)
if not v_fmt:
    v_fmt = next((f for f in info['formats'] if f.get('height') and f.get('height') >= 1070 and f.get('vcodec') != 'none' and f.get('protocol') == 'https'), None)

a_fmt = next((f for f in info['formats'] if f.get('format_id') == '140'), None)
if not a_fmt:
    a_fmt = next((f for f in info['formats'] if f.get('vcodec') == 'none' and f.get('acodec') != 'none' and f.get('protocol') == 'https'), None)

with open("live3_work/stream_url_1080p.txt", "w") as f:
    f.write(v_fmt['url'])
with open("live3_work/stream_url_audio.txt", "w") as f:
    f.write(a_fmt['url'])

print(f"\nSelected Video: {v_fmt['format_id']} ({v_fmt.get('resolution')} @ {v_fmt.get('fps')}fps, {v_fmt.get('vcodec')})")
print(f"Selected Audio: {a_fmt['format_id']} ({a_fmt.get('acodec')})")

comments = info.get('comments', [])
print(f"Total comments fetched: {len(comments)}")
with open("live3_work/top_comments.json", "w", encoding="utf-8") as f:
    json.dump([{'author': c.get('author'), 'text': c.get('text'), 'likes': c.get('like_count')} for c in comments], f, indent=2)

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
print(f"Timestamp lines found: {len(lines)}")
for likes, author, line in lines[:60]:
    t = parse_time(line)
    if t <= (info.get("duration") or 999999):
        print(f"[{t:5d}s | {author}]: {line[:120]}")
