import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

os.makedirs("sfx_pack", exist_ok=True)
SR = 48000

def save_wav(filename, data):
    peak = np.max(np.abs(data))
    if peak > 0:
        data = data / peak * 0.9
    pcm = np.int16(data * 32767)
    wavfile.write(os.path.join("sfx_pack", filename), SR, pcm)

# 1. Whoosh SFX (0.45s swept bandpass noise)
dur = 0.45
t = np.linspace(0, dur, int(SR * dur), endpoint=False)
noise = np.random.randn(len(t))
env = np.sin(np.pi * t / dur) ** 1.5
# Lowpass sweep approximation
b, a = butter(2, [300 / (SR / 2), 2800 / (SR / 2)], btype='band')
whoosh = lfilter(b, a, noise) * env
save_wav("whoosh.wav", whoosh)

# 2. Sub-Bass Impact / Vine-style Boom (0.65s)
dur_b = 0.65
tb = np.linspace(0, dur_b, int(SR * dur_b), endpoint=False)
freq_b = 110 * np.exp(-6.0 * tb) + 38
boom = np.sin(2 * np.pi * np.cumsum(freq_b) / SR) * np.exp(-4.5 * tb)
save_wav("bass_drop.wav", boom)

# 3. Clean UI Pop (0.12s)
dur_p = 0.12
tp = np.linspace(0, dur_p, int(SR * dur_p), endpoint=False)
freq_p = 450 + 650 * np.exp(-28 * tp)
pop = np.sin(2 * np.pi * np.cumsum(freq_p) / SR) * np.exp(-30 * tp)
save_wav("pop.wav", pop)

# 4. Tension Riser (1.2s)
dur_r = 1.2
tr = np.linspace(0, dur_r, int(SR * dur_r), endpoint=False)
freq_r = 180 + 700 * (tr / dur_r) ** 2
riser = np.sin(2 * np.pi * np.cumsum(freq_r) / SR) * (tr / dur_r) ** 1.8 * 0.6
save_wav("riser.wav", riser)

print("Generated sfx_pack: whoosh.wav, bass_drop.wav, pop.wav, riser.wav")
