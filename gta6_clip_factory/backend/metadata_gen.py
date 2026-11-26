from typing import Dict, Any
from .models import CandidateClip


def generate_clip_metadata(clip: CandidateClip) -> Dict[str, Any]:
    dur_s = int(round(clip.duration))
    score = clip.heuristic_score
    sig = clip.signals

    if sig.audio_peak >= 0.55 and sig.motion_score >= 0.55:
        angle = "Chaotic Action & Reaction"
    elif sig.audio_peak >= 0.55:
        angle = "Loud Reaction / Dialogue Highlight"
    elif sig.motion_score >= 0.55:
        angle = "High-Speed Gameplay Moment"
    else:
        angle = "Vice City Gameplay Moment"

    titles = [
        f"GTA VI {angle} ({dur_s}s Clip) | {clip.source_filename}",
        f"Unbelievable Moment in Leonida — {angle}",
        f"GTA 6 Gameplay Highlight: {clip.editor.hook_text or angle}",
    ]

    caption = (
        f"Captured from local gameplay ({clip.start_time:.1f}s – {clip.end_time:.1f}s). "
        f"Signal note: {clip.rationale}"
    )

    keywords = [
        "GTA VI", "GTA 6", "Grand Theft Auto VI", "GTA 6 Gameplay",
        "Vice City", "Leonida", "Gaming Shorts", "Vertical Gameplay",
    ]
    hashtags = ["#GTA6", "#GTAVI", "#GTA6Gameplay", "#ViceCity", "#GamingShorts"]

    return {
        "titles": titles,
        "caption": caption,
        "keywords": keywords,
        "hashtags": hashtags,
        "heuristic_score": score,
        "disclaimer": (
            "Notice: Heuristic scores, title options, and hashtags do not guarantee reach or virality. "
            "Copyrighted game footage and in-game music may be subject to publisher rules, platform copyright "
            "claims, and monetization restrictions. Adding captions, filters, or credits does not establish permission."
        ),
    }
