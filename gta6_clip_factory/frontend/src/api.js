const API_BASE = '/api';

async function req(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const err = await res.json();
      msg = err.detail || msg;
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const api = {
  health: () => req('/system/health'),
  getSettings: () => req('/settings'),
  saveSettings: (data) => req('/settings', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }),
  listRecordings: () => req('/recordings'),
  importYoutube: (url) => req('/youtube/import', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url }) }),
  importPaths: (paths) => req('/recordings/import', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ paths }) }),
  uploadFile: (file) => {
    const fd = new FormData();
    fd.append('file', file);
    return req('/recordings/upload', { method: 'POST', body: fd });
  },
  deleteRecording: (id) => req(`/recordings/${id}`, { method: 'DELETE' }),
  runAnalysis: (payload) => req('/analysis/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  listCandidates: () => req('/candidates'),
  updateCandidate: (id, patch) => req(`/candidates/${id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(patch) }),
  regenMetadata: (id) => req(`/candidates/${id}/metadata`, { method: 'POST' }),
  batchExport: (payload) => req('/exports/batch', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }),
  listExports: () => req('/exports'),
  cancelExport: (id) => req(`/exports/${id}/cancel`, { method: 'POST' }),
  retryExport: (id) => req(`/exports/${id}/retry`, { method: 'POST' }),
};
