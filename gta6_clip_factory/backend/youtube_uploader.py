import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
ROOT = Path(__file__).resolve().parent.parent
CLIENT_SECRETS = ROOT / "projects" / "client_secrets.json"
TOKEN_FILE = ROOT / "projects" / "token.json"
EXPORTS_DIR = ROOT / "media" / "exports"
THUMBS_DIR = ROOT / "media" / "thumbnails"
UPLOAD_LOG = ROOT / "projects" / "uploaded_history.json"


def get_youtube_service():
    if not CLIENT_SECRETS.exists():
        raise FileNotFoundError(
            f"Missing {CLIENT_SECRETS}. Download OAuth Desktop App JSON from Google Cloud Console and save it there."
        )
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def upload_short(
    youtube,
    video_path: Path,
    title: str,
    description: str,
    tags: list,
    thumbnail_path: Optional[Path] = None,
    publish_at_iso: Optional[str] = None,
):
    status = {"selfDeclaredMadeForKids": False}
    if publish_at_iso:
        status["privacyStatus"] = "private"
        status["publishAt"] = publish_at_iso
    else:
        status["privacyStatus"] = "private"

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:4900],
            "tags": tags[:15],
            "categoryId": "20",  # Gaming
        },
        "status": status,
    }
    media = MediaFileUpload(str(video_path), chunksize=4 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        _, resp = req.next_chunk()

    vid_id = resp["id"]
    if thumbnail_path and thumbnail_path.exists():
        try:
            youtube.thumbnails().set(videoId=vid_id, media_body=MediaFileUpload(str(thumbnail_path))).execute()
        except Exception as e:
            print(f"[WARN] Thumbnail set skipped for {vid_id}: {e}")
    return vid_id


def main():
    parser = argparse.ArgumentParser(description="Scheduled YouTube Shorts Uploader for VicePulse")
    parser.add_argument("--limit", type=int, default=3, help="Max Shorts to upload per run (recommended: 2-3/day)")
    parser.add_argument("--interval-hours", type=int, default=5, help="Hours between scheduled publishAt times")
    args = parser.parse_args()

    history = json.loads(UPLOAD_LOG.read_text(encoding="utf-8")) if UPLOAD_LOG.exists() else {}
    yt = get_youtube_service()

    mp4s = sorted(EXPORTS_DIR.glob("*.mp4"))
    uploaded_now = 0
    base_time = datetime.now(timezone.utc) + timedelta(hours=1)

    for mp4 in mp4s:
        if mp4.name in history:
            continue
        if uploaded_now >= args.limit:
            break

        title = f"{mp4.stem.replace('_', ' ')} | GTA 6 Gameplay #Shorts #GTA6"
        desc = "Edited in 1080p60 with commentary & sound design. #GTA6 #GTAVI #GamingShorts #ViceCity"
        tags = ["GTA 6", "GTA VI", "GTA 6 Shorts", "Gaming Shorts", "Vice City"]
        thumb = THUMBS_DIR / f"{mp4.stem}.jpg"
        pub_iso = (base_time + timedelta(hours=args.interval_hours * uploaded_now)).strftime("%Y-%m-%dT%H:%M:%SZ")

        print(f"Uploading {mp4.name} (scheduled {pub_iso})...")
        vid_id = upload_short(yt, mp4, title, desc, tags, thumb if thumb.exists() else None, pub_iso)
        history[mp4.name] = {"video_id": vid_id, "publish_at": pub_iso}
        UPLOAD_LOG.write_text(json.dumps(history, indent=2), encoding="utf-8")
        print(f"Uploaded: https://youtu.be/{vid_id}")
        uploaded_now += 1

    print(f"Done. Uploaded {uploaded_now} Short(s).")


if __name__ == "__main__":
    main()
