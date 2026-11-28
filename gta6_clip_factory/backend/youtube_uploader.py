import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .media_probe import probe_video_file

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parent
CLIENT_SECRETS = ROOT / "projects" / "client_secrets.json"
TOKEN_FILE = ROOT / "projects" / "token.json"
EXPORTS_DIR = ROOT / "media" / "exports"
THUMBS_DIR = ROOT / "media" / "thumbnails"
UPLOAD_LOG = ROOT / "projects" / "uploaded_history.json"

# 3 optimal global/IST slots per day from research.md (UTC equivalents):
# 01:00 UTC (6:30 AM IST - US evening), 14:00 UTC (7:30 PM IST - India/EU), 17:30 UTC (11:00 PM IST - EU/US morning)
DAILY_UTC_SLOTS = [(1, 0), (14, 0), (17, 30)]


def load_viral_metadata_lookup() -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    csv_paths = [
        WORKSPACE / "IShowSpeed_PRO_REELS" / "METADATA" / "youtube_upload_details.csv",
        WORKSPACE / "TECHNO_GAMERZ_REELS" / "METADATA" / "youtube_upload_details.csv",
    ]
    for cp in csv_paths:
        if not cp.exists():
            continue
        with cp.open("r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                fname = (row.get("Filename") or "").strip()
                if not fname:
                    continue
                entry = {
                    "title": (row.get("Title") or "").strip(),
                    "description": (row.get("Description") or "").strip(),
                    "hashtags": (row.get("Hashtags") or "").strip(),
                    "score": float(row.get("Viral Score") or 90),
                }
                lookup[fname] = entry
                if fname.startswith("Techno_Reel_"):
                    lookup[f"Pro_{fname}"] = entry
    return lookup


def get_youtube_service():
    if not CLIENT_SECRETS.exists():
        raise FileNotFoundError(f"Missing {CLIENT_SECRETS}.")
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


def assert_portrait_short(video_path: Path) -> None:
    info = probe_video_file(str(video_path))
    w, h = info["width"], info["height"]
    if w >= h or w != 1080 or h != 1920:
        raise ValueError(f"Rejected {video_path.name}: expected 1080x1920 portrait Short, got {w}x{h}.")
    if info["duration"] > 60.0:
        raise ValueError(f"Rejected {video_path.name}: duration {info['duration']}s exceeds 60s Short limit.")


def compute_schedule_slots(already_uploaded_count: int, count: int) -> List[str]:
    now = datetime.now(timezone.utc)
    # Generate upcoming slots starting from tomorrow (or later today if slot > now + 30m)
    slots: List[datetime] = []
    day_offset = 0
    while len(slots) < already_uploaded_count + count + 6:
        day_base = (now + timedelta(days=day_offset)).replace(minute=0, second=0, microsecond=0)
        for hr, mn in DAILY_UTC_SLOTS:
            candidate = day_base.replace(hour=hr, minute=mn)
            if candidate > now + timedelta(minutes=30):
                slots.append(candidate)
        day_offset += 1

    picked = slots[already_uploaded_count : already_uploaded_count + count]
    return [dt.strftime("%Y-%m-%dT%H:%M:%SZ") for dt in picked]


def upload_short(
    youtube,
    video_path: Path,
    title: str,
    description: str,
    tags: list,
    thumbnail_path: Optional[Path] = None,
    publish_at_iso: Optional[str] = None,
):
    assert_portrait_short(video_path)

    # Ensure #Shorts is present for Shorts shelf indexing
    if "#Shorts" not in title and "#shorts" not in title.lower():
        title = f"{title[:90]} #Shorts"

    status = {"selfDeclaredMadeForKids": False, "privacyStatus": "private"}
    if publish_at_iso:
        status["publishAt"] = publish_at_iso

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:4900],
            "tags": tags[:15],
            "categoryId": "20",
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
    parser = argparse.ArgumentParser(description="Viral-Ranked Portrait YouTube Shorts Scheduler (3/day)")
    parser.add_argument("--limit", type=int, default=5, help="Max Shorts to upload in this run (quota allows ~6/day)")
    args = parser.parse_args()

    history = json.loads(UPLOAD_LOG.read_text(encoding="utf-8")) if UPLOAD_LOG.exists() else {}
    meta_lookup = load_viral_metadata_lookup()

    # Rank all un-uploaded, advertiser-safe portrait MP4s by viral score descending
    # Exclude mature/suggestive clips so the channel stays monetizable & Shorts-feed eligible
    blocked_mature = {"Speed_Reel_005.mp4", "Speed_Reel_006.mp4"}
    candidates = []
    for mp4 in EXPORTS_DIR.glob("*.mp4"):
        if mp4.name in history or mp4.name in blocked_mature:
            continue
        try:
            assert_portrait_short(mp4)
        except Exception as e:
            print(f"[SKIP] {e}")
            continue
        m = meta_lookup.get(mp4.name, {})
        score = m.get("score", 85.0)
        candidates.append((score, mp4, m))

    candidates.sort(key=lambda x: x[0], reverse=True)
    to_upload = candidates[: args.limit]
    if not to_upload:
        print("No new portrait Shorts left to upload.")
        return

    slots = compute_schedule_slots(len(history), len(to_upload))
    yt = get_youtube_service()

    for (score, mp4, m), pub_iso in zip(to_upload, slots):
        title = m.get("title") or f"{mp4.stem.replace('_', ' ')} | GTA 6 Gameplay #Shorts"
        hashtags = m.get("hashtags") or "#GTA6 #GTAVI #Shorts #ViceCity #GamingShorts"
        desc = m.get("description") or "Edited in 1080p60 portrait with commentary & sound design."
        full_desc = f"{desc}\n\n{hashtags}\n#Shorts"
        tags = ["GTA 6", "GTA VI", "GTA 6 Shorts", "GTA 6 Gameplay", "Vice City", "Gaming Shorts"]
        thumb = THUMBS_DIR / f"{mp4.stem}.jpg"

        print(f"[Score {score}] Uploading {mp4.name} -> scheduled {pub_iso}...")
        vid_id = upload_short(yt, mp4, title, full_desc, tags, thumb if thumb.exists() else None, pub_iso)
        history[mp4.name] = {"video_id": vid_id, "publish_at": pub_iso, "score": score, "title": title}
        UPLOAD_LOG.write_text(json.dumps(history, indent=2), encoding="utf-8")
        print(f"  -> Uploaded: https://youtu.be/{vid_id}")

    print(f"Completed {len(to_upload)} scheduled portrait upload(s)!")


if __name__ == "__main__":
    main()
