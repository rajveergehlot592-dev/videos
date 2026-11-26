from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


LayoutType = Literal["dynamic_crop", "blurred_bg", "manual_crop"]


class CaptionSegment(BaseModel):
    start: float
    end: float
    text: str


class EditorConfig(BaseModel):
    layout: LayoutType = "blurred_bg"
    track_x: float = Field(0.5, ge=0.0, le=1.0)
    track_y: float = Field(0.5, ge=0.0, le=1.0)
    zoom: float = Field(1.0, ge=1.0, le=2.0)
    crop_x: float = Field(0.15, ge=0.0, le=0.95)
    crop_y: float = Field(0.0, ge=0.0, le=0.95)
    crop_w: float = Field(0.70, ge=0.05, le=1.0)
    crop_h: float = Field(1.0, ge=0.05, le=1.0)
    bg_blur: int = Field(22, ge=0, le=50)
    bg_darken: float = Field(0.35, ge=0.0, le=0.85)
    hook_text: str = ""
    hook_enabled: bool = True
    captions_enabled: bool = True
    captions: List[CaptionSegment] = Field(default_factory=list)
    font_name: str = "Arial"
    font_size: int = Field(52, ge=24, le=96)
    text_color: str = "#FFFFFF"
    highlight_color: str = "#FFE600"
    safe_margin_bottom: int = Field(210, ge=60, le=450)
    effect_color_boost: bool = False
    effect_progress_bar: bool = True
    effect_loudnorm: bool = True
    fps: int = Field(30, ge=24, le=60)
    crf: int = Field(20, ge=14, le=30)


class RecordingMetadata(BaseModel):
    id: str
    filename: str
    filepath: str
    file_hash: str
    size_bytes: int
    duration: float
    width: int
    height: int
    fps: float
    rotation: int = 0
    vcodec: str
    acodec: Optional[str] = None
    has_audio: bool = True
    audio_sample_rate: Optional[int] = None
    audio_channels: Optional[int] = None
    thumbnail_url: Optional[str] = None
    status: str = "imported"
    imported_at: str


class SignalBreakdown(BaseModel):
    audio_peak: float = 0.0
    motion_score: float = 0.0
    scene_change: float = 0.0
    speech_event: float = 0.0


class CandidateClip(BaseModel):
    id: str
    recording_id: str
    source_filename: str
    start_time: float
    end_time: float
    duration: float
    heuristic_score: float
    rationale: str
    signals: SignalBreakdown = Field(default_factory=SignalBreakdown)
    thumbnail_url: Optional[str] = None
    status: Literal["pending", "approved", "rejected"] = "pending"
    editor: EditorConfig = Field(default_factory=EditorConfig)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExportJob(BaseModel):
    id: str
    clip_id: str
    recording_id: str
    output_filename: str
    output_path: Optional[str] = None
    srt_path: Optional[str] = None
    status: Literal["queued", "running", "completed", "failed", "cancelled"] = "queued"
    progress: float = 0.0
    error: Optional[str] = None
    duration_verified: Optional[float] = None
    resolution_verified: Optional[str] = None
    has_audio_verified: Optional[bool] = None
    created_at: str
    completed_at: Optional[str] = None


class ImportPathsRequest(BaseModel):
    paths: List[str]


class AnalyzeRequest(BaseModel):
    recording_id: str
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    pre_padding: Optional[float] = None
    post_padding: Optional[float] = None
    merge_gap: Optional[float] = None


class BatchExportRequest(BaseModel):
    clip_ids: List[str]
    fps: Optional[int] = None
    crf: Optional[int] = None
