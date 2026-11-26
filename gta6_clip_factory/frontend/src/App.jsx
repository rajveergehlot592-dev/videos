import React, { useEffect, useState } from 'react';
import {
  Youtube, Sparkles, Upload, Play, Check, X, Download,
  Wand2, Volume2, Sliders, RefreshCw, Ban, Flame
} from 'lucide-react';
import { api } from './api.js';

export default function App() {
  const [ytUrl, setYtUrl] = useState('');
  const [autoRenderTop, setAutoRenderTop] = useState(true);
  const [fetchingYt, setFetchingYt] = useState(false);
  const [recordings, setRecordings] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [exportsList, setExportsList] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [viewMode, setViewMode] = useState('editor');
  const [toast, setToast] = useState('');
  const [error, setError] = useState('');

  const notify = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3500);
  };

  const refreshAll = async () => {
    try {
      const [r, c, e] = await Promise.all([api.listRecordings(), api.listCandidates(), api.listExports()]);
      setRecordings(r);
      setCandidates(c);
      setExportsList(e);
      if (!activeId && c.length > 0) {
        setActiveId(c[0].id);
        if (e.some((j) => j.clip_id === c[0].id && j.status === 'completed')) {
          setViewMode('rendered');
        }
      }
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => { refreshAll(); }, []);

  useEffect(() => {
    const busy = exportsList.some((j) => j.status === 'queued' || j.status === 'running');
    if (!busy) return;
    const t = setInterval(() => api.listExports().then(setExportsList).catch(() => {}), 1500);
    return () => clearInterval(t);
  }, [exportsList]);

  const activeClip = candidates.find((c) => c.id === activeId) || candidates[0] || null;
  const latestExport = activeClip
    ? exportsList.find((j) => j.clip_id === activeClip.id && j.status === 'completed')
    : null;
  const approvedClips = candidates.filter((c) => c.status === 'approved');

  const handleYoutubeIngest = async (e) => {
    e.preventDefault();
    if (!ytUrl.trim()) return;
    setFetchingYt(true);
    setError('');
    try {
      const res = await api.importYoutube(ytUrl.trim());
      notify(`Extracted ${res.candidates.length} viral moments from ${res.recording.uploader}!`);
      setYtUrl('');
      await refreshAll();
      if (res.candidates.length > 0) {
        setActiveId(res.candidates[0].id);
        if (autoRenderTop) {
          const topIds = res.candidates.slice(0, 3).map((c) => c.id);
          await api.batchExport({ clip_ids: topIds });
          notify(`Auto-rendering top ${topIds.length} 1080p60 Pro Reels with VO, SFX & Captions!`);
          setExportsList(await api.listExports());
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setFetchingYt(false);
    }
  };

  const handleLocalUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFetchingYt(true);
    setError('');
    try {
      const res = await api.uploadFile(file);
      const rec = res.imported?.[0];
      if (rec) {
        const ana = await api.runAnalysis({ recording_id: rec.id });
        notify(`Imported & found ${ana.candidates.length} highlights!`);
        await refreshAll();
        if (ana.candidates.length > 0) setActiveId(ana.candidates[0].id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setFetchingYt(false);
    }
  };

  const patchClip = async (id, patch) => {
    try {
      const upd = await api.updateCandidate(id, patch);
      setCandidates((prev) => prev.map((c) => (c.id === id ? upd : c)));
    } catch (err) {
      setError(err.message);
    }
  };

  const renderClips = async (ids) => {
    if (!ids.length) return setError('Approve or select a clip first.');
    setError('');
    try {
      const res = await api.batchExport({ clip_ids: ids });
      notify(`Rendering ${res.queued} 1080p60 Pro Reel(s)...`);
      setExportsList(await api.listExports());
    } catch (err) {
      setError(err.message);
    }
  };

  const fmtTime = (sec) => {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = Math.floor(sec % 60);
    return h > 0 ? `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}` : `${m}:${String(s).padStart(2, '0')}`;
  };

  return (
    <div className="studio">
      <header className="hero-bar">
        <div className="brand">
          <span className="brand-vi">VI</span>
          <span>CLIP FACTORY <span style={{ color: 'var(--cyan)', fontSize: 11 }}>PRO</span></span>
        </div>

        <form className="yt-ingest" onSubmit={handleYoutubeIngest}>
          <Youtube size={18} color="#ff2a85" />
          <input
            placeholder="Paste any YouTube Video or Livestream URL (e.g. https://youtu.be/... or /live/...)"
            value={ytUrl}
            onChange={(e) => setYtUrl(e.target.value)}
          />
          <label style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: 'var(--muted)', whiteSpace: 'nowrap', cursor: 'pointer' }}>
            <input type="checkbox" checked={autoRenderTop} onChange={(e) => setAutoRenderTop(e.target.checked)} /> Auto-Render Top 3
          </label>
          <button className="btn btn-glow" type="submit" disabled={fetchingYt}>
            <Sparkles size={14} /> {fetchingYt ? 'Scanning Stream...' : 'Find Viral Moments'}
          </button>
        </form>

        <label className="btn" style={{ cursor: 'pointer' }}>
          <Upload size={14} /> Local File
          <input type="file" accept="video/*" hidden onChange={handleLocalUpload} />
        </label>

        <button className="btn btn-cyan" onClick={() => renderClips(approvedClips.map((c) => c.id))}>
          <Flame size={14} /> Export Approved ({approvedClips.length})
        </button>
      </header>

      {(toast || error) && (
        <div style={{ padding: '8px 22px', background: error ? 'rgba(255,61,90,0.16)' : 'rgba(0,230,118,0.14)', borderBottom: '1px solid var(--border)', fontSize: 12, fontWeight: 700, color: error ? '#ff8a9e' : 'var(--green)', display: 'flex', justifyContent: 'space-between' }}>
          <span>{error || toast}</span>
          {error && <button className="btn" style={{ padding: '2px 8px' }} onClick={() => setError('')}>Dismiss</button>}
        </div>
      )}

      <div className="workspace">
        <section className="col col-left">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="lbl">Viral Moments ({candidates.length})</span>
            <span style={{ fontSize: 11, color: 'var(--muted)' }}>{recordings.length} source(s)</span>
          </div>

          {candidates.length === 0 ? (
            <div className="section-box" style={{ textAlign: 'center', padding: 28, color: 'var(--muted)', fontSize: 13 }}>
              Paste a YouTube URL above to auto-detect 1080p60 viral highlights, or upload a local video.
            </div>
          ) : (
            candidates.map((c) => (
              <div
                key={c.id}
                className={`clip-card ${activeClip?.id === c.id ? 'active' : ''}`}
                onClick={() => { setActiveId(c.id); setViewMode('editor'); }}
              >
                <img className="clip-thumb" src={c.thumbnail_url || ''} alt="" />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', gap: 6, marginBottom: 4 }}>
                    <span className="pill pill-gold">★ {c.heuristic_score}</span>
                    <span className={`pill ${c.status === 'approved' ? 'pill-green' : c.status === 'rejected' ? 'pill-red' : ''}`}>
                      {c.status.toUpperCase()}
                    </span>
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {c.editor?.hook_text || c.source_filename}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--cyan)', marginTop: 2 }}>
                    ⏱ {fmtTime(c.start_time)} → {fmtTime(c.end_time)} ({c.duration}s)
                  </div>
                </div>
              </div>
            ))
          )}
        </section>

        <section className="col col-center">
          {!activeClip ? (
            <div style={{ textAlign: 'center', maxWidth: 420 }}>
              <h2 style={{ fontSize: 22, fontWeight: 900, marginBottom: 8 }}>GTA VI Viral Clip Studio</h2>
              <p style={{ color: 'var(--muted)', fontSize: 13, lineHeight: 1.6 }}>
                Paste any YouTube livestream or gameplay link in the top bar. We pull the 1080p60 stream, detect viral community moments, and render copyright-safe Reels with neural voiceovers, studio SFX, and pop captions.
              </p>
            </div>
          ) : (
            <>
              <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
                <button className={`btn ${viewMode === 'editor' ? 'btn-cyan' : ''}`} onClick={() => setViewMode('editor')}>
                  <Sliders size={13} /> Live Studio Preview
                </button>
                <button className={`btn ${viewMode === 'rendered' ? 'btn-glow' : ''}`} disabled={!latestExport} onClick={() => setViewMode('rendered')}>
                  <Play size={13} /> {latestExport ? 'Play Rendered 1080p60 MP4' : 'Not Rendered Yet'}
                </button>
              </div>

              <div className="phone-bezel">
                {viewMode === 'rendered' && latestExport ? (
                  <video
                    key={latestExport.output_filename}
                    src={`/api/files/exports/${latestExport.output_filename}`}
                    controls
                    autoPlay
                    playsInline
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  <>
                    {activeClip.thumbnail_url && <img className="phone-bg" src={activeClip.thumbnail_url} alt="" />}
                    <div className="phone-fg" style={{ filter: activeClip.editor.effect_color_boost ? 'contrast(1.08) saturate(1.15)' : 'none' }}>
                      {activeClip.thumbnail_url && (
                        <img
                          src={activeClip.thumbnail_url}
                          alt=""
                          style={{
                            width: '100%',
                            height: activeClip.editor.layout === 'blurred_bg' ? '56%' : '100%',
                            objectFit: activeClip.editor.layout === 'blurred_bg' ? 'contain' : 'cover',
                            objectPosition: `${activeClip.editor.track_x * 100}% ${activeClip.editor.track_y * 100}%`,
                            borderRadius: activeClip.editor.layout === 'blurred_bg' ? 8 : 0,
                          }}
                        />
                      )}
                    </div>
                    {activeClip.editor.hook_enabled && (
                      <div className="hook-banner" style={{ color: activeClip.editor.highlight_color }}>
                        {activeClip.editor.hook_text}
                      </div>
                    )}
                    {activeClip.editor.captions_enabled && (
                      <div className="caption-preview" style={{ bottom: Math.round(activeClip.editor.safe_margin_bottom / 3.5), color: activeClip.editor.text_color }}>
                        <span style={{ color: activeClip.editor.highlight_color }}>
                          {(activeClip.editor.captions?.[0]?.text || 'WAIT FOR THIS!').split(' ')[0]}{' '}
                        </span>
                        {(activeClip.editor.captions?.[0]?.text || 'WAIT FOR THIS!').split(' ').slice(1).join(' ')}
                      </div>
                    )}
                    {activeClip.editor.effect_progress_bar && (
                      <div style={{ position: 'absolute', bottom: 0, left: 0, width: '68%', height: 5, background: 'var(--yellow)', zIndex: 6 }} />
                    )}
                  </>
                )}
              </div>

              <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
                <button className="btn btn-green" onClick={() => patchClip(activeClip.id, { status: 'approved' })}><Check size={14} /> Approve</button>
                <button className="btn btn-red" onClick={() => patchClip(activeClip.id, { status: 'rejected' })}><X size={14} /> Reject</button>
                <button className="btn btn-glow" onClick={() => renderClips([activeClip.id])}><Wand2 size={14} /> Render 1080p60 Pro Reel</button>
              </div>
            </>
          )}
        </section>

        <section className="col col-right">
          {activeClip && (
            <>
              <div className="section-box">
                <span className="lbl">Cut & Layout</span>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  <div>
                    <span className="lbl">Start (s)</span>
                    <input className="ctrl" type="number" step="1" value={activeClip.start_time} onChange={(e) => patchClip(activeClip.id, { start_time: Number(e.target.value) })} />
                  </div>
                  <div>
                    <span className="lbl">End (s)</span>
                    <input className="ctrl" type="number" step="1" value={activeClip.end_time} onChange={(e) => patchClip(activeClip.id, { end_time: Number(e.target.value) })} />
                  </div>
                </div>
                <select className="ctrl" value={activeClip.editor.layout} onChange={(e) => patchClip(activeClip.id, { editor: { layout: e.target.value } })}>
                  <option value="blurred_bg">Centered HD + Blurred Studio BG</option>
                  <option value="dynamic_crop">Dynamic Vertical 9:16 Crop</option>
                  <option value="manual_crop">Manual Crop</option>
                </select>
              </div>

              <div className="section-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="lbl"><Volume2 size={11} /> Neural Voiceover + SFX (Anti-Copyright)</span>
                  <input
                    type="checkbox"
                    checked={Boolean(activeClip.metadata?.pro_mode)}
                    onChange={(e) => patchClip(activeClip.id, { metadata: { pro_mode: e.target.checked } })}
                  />
                </div>
                <select
                  className="ctrl"
                  value={activeClip.metadata?.vo_voice || 'en-US-AndrewMultilingualNeural'}
                  onChange={(e) => patchClip(activeClip.id, { metadata: { vo_voice: e.target.value } })}
                >
                  <option value="en-US-AndrewMultilingualNeural">Andrew (Energetic US Creator)</option>
                  <option value="en-IN-PrabhatNeural">Prabhat (Indian English Creator)</option>
                  <option value="en-US-GuyNeural">Guy (Punchy Gaming Narrator)</option>
                </select>
                <textarea
                  className="ctrl"
                  rows={2}
                  placeholder="Opening voiceover hook..."
                  value={activeClip.metadata?.vo_script || ''}
                  onChange={(e) => patchClip(activeClip.id, { metadata: { vo_script: e.target.value } })}
                />
              </div>

              <div className="section-box">
                <span className="lbl">Hook & Pop Captions</span>
                <input
                  className="ctrl"
                  value={activeClip.editor.hook_text}
                  onChange={(e) => patchClip(activeClip.id, { editor: { hook_text: e.target.value } })}
                />
                <div style={{ display: 'flex', gap: 10, fontSize: 11, flexWrap: 'wrap' }}>
                  <label><input type="checkbox" checked={activeClip.editor.effect_color_boost} onChange={(e) => patchClip(activeClip.id, { editor: { effect_color_boost: e.target.checked } })} /> Color Boost</label>
                  <label><input type="checkbox" checked={activeClip.editor.effect_progress_bar} onChange={(e) => patchClip(activeClip.id, { editor: { effect_progress_bar: e.target.checked } })} /> Progress Bar</label>
                  <label><input type="checkbox" checked={activeClip.editor.captions_enabled} onChange={(e) => patchClip(activeClip.id, { editor: { captions_enabled: e.target.checked } })} /> Captions</label>
                </div>
              </div>
            </>
          )}

          <div className="section-box">
            <span className="lbl">All Rendered Files & Queue ({exportsList.length})</span>
            {exportsList.length === 0 ? (
              <span style={{ fontSize: 12, color: 'var(--muted)' }}>Click "Render 1080p60 Pro Reel" to export.</span>
            ) : (
              exportsList.map((j) => (
                <div key={j.id} style={{ padding: 8, borderRadius: 9, background: 'rgba(0,0,0,0.35)', border: '1px solid var(--border)', fontSize: 11, display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 6 }}>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{j.output_filename}</div>
                    <div style={{ color: j.status === 'completed' ? 'var(--green)' : j.status === 'failed' ? 'var(--red)' : 'var(--yellow)' }}>
                      {j.status.toUpperCase()} {j.resolution_verified ? `• ${j.resolution_verified}` : ''}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 4 }}>
                    {(j.status === 'queued' || j.status === 'running') && (
                      <button className="btn btn-red" style={{ padding: '4px 7px' }} onClick={() => api.cancelExport(j.id).then(refreshAll)}><Ban size={11} /></button>
                    )}
                    {(j.status === 'failed' || j.status === 'cancelled') && (
                      <button className="btn" style={{ padding: '4px 7px' }} onClick={() => api.retryExport(j.id).then(refreshAll)}><RefreshCw size={11} /></button>
                    )}
                    {j.status === 'completed' && (
                      <>
                        <button className="btn btn-cyan" style={{ padding: '4px 8px' }} onClick={() => { setActiveId(j.clip_id); setViewMode('rendered'); }}><Play size={11} /></button>
                        <a className="btn btn-green" style={{ padding: '4px 8px' }} href={`/api/files/exports/${j.output_filename}`} download><Download size={11} /></a>
                      </>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
