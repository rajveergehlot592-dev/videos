import yt_dlp
import json

ydl_opts = {
    'getcomments': True,
    'skip_download': True,
    'extractor_args': {'youtube': {'max_comments': ['200', 'all', '100', '0']}}
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info('https://www.youtube.com/live/irNhWMG560k', download=False)
        comments = info.get('comments', [])
        print(f"Total comments fetched: {len(comments)}")
        
        timestamp_comments = []
        for c in comments:
            text = c.get('text', '')
            if ':' in text and any(ch.isdigit() for ch in text):
                timestamp_comments.append((c.get('author'), text))
                
        print(f"Comments containing timestamps: {len(timestamp_comments)}")
        for author, text in timestamp_comments[:15]:
            print(f"\n[Author: {author}]")
            print(text[:500])
            
        with open('comments_dump.json', 'w', encoding='utf-8') as f:
            json.dump([{'author': c.get('author'), 'text': c.get('text'), 'like_count': c.get('like_count')} for c in comments], f, indent=2)
except Exception as e:
    print("Error fetching comments:", e)
