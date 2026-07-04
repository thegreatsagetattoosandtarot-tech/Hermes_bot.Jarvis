#!/usr/bin/env python3
"""
JARVIS TTS — Kokoro-powered British male voice (bm_george).
Modeled after J.A.R.V.I.S. from Iron Man/Avengers (Paul Bettany).
Calm, precise, British, crisp and confident, authoritative butler tone.

Refined for maximum cinematic polish:
  - Speed 0.95 for crisp, confident delivery (film JARVIS speaks at a natural conversational pace)
  - Post-processing: high-pass filter (150Hz), presence boost (3-6kHz +2dB), light compression, subtle reverb (6% wet), -3dB normalization
  - SSML-style text preprocessing for natural pacing
  - 192kbps MP3 output

Usage:
    python3 jarvis_tts.py "Your text here"
    echo "Your text here" | python3 jarvis_tts.py

Output:
    Prints the path to the generated MP3 file (e.g. /data/workspace/jarvis_20240101_120000.mp3)
    Hermes can then use: MEDIA:./jarvis_20240101_120000.mp3
"""

import sys
import os
import re
import numpy as np
import soundfile as sf
from datetime import datetime

# --- JARVIS VOICE PROFILE ---
JARVIS_VOICE  = 'bm_george'    # British male — closest to Paul Bettany's JARVIS
JARVIS_SPEED  = 1.02            # Crisp, confident pace — film JARVIS is quick, not slow
JARVIS_LANG   = 'b'            # 'b' = British English phoneme set
WORKSPACE     = '/data/workspace'
SAMPLE_RATE   = 24000           # Kokoro native sample rate

# --- POST-PROCESSING SETTINGS ---
HIGHPASS_HZ   = 150             # High-pass cutoff: removes low-end muddiness below 150Hz (tighter clarity)
PRESENCE_GAIN_DB = 3.0          # +3dB shelf boost in 3kHz-6kHz 'clarity band' for consonant definition
REVERB_DECAY  = 0.015           # ~15ms reverb tail (very subtle spatial depth)
REVERB_MIX    = 0.06            # Wet/dry mix for reverb (6% wet = barely perceptible shimmer)
PEAK_TARGET   = -3.0            # Target peak dBFS for final normalization
OUTPUT_KBPS   = '192k'          # MP3 bitrate


# ---------------------------------------------------------------------------
# TEXT PREPROCESSING
# ---------------------------------------------------------------------------

def preprocess_text(text: str) -> str:
    """SSML-style text preprocessing for natural JARVIS pacing.

    - Cleans up stray whitespace and HTML artifacts
    - Inserts Kokoro-friendly pause markers after commas for rhythmic breathing
    - Ensures ellipses produce natural pauses
    - Expands common abbreviations for cleaner phoneme rendering
    """
    # Strip HTML tags / SSML remnants
    text = re.sub(r'<[^>]+>', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Expand common abbreviations that TTS models often mispronounce
    abbrevs = {
        r'\bSir\b':    'Sir',          # Keep as-is — Kokoro handles it well
        r'\bDr\.\s':   'Doctor ',
        r'\bMr\.\s':   'Mister ',
        r'\bMrs\.\s':  'Missus ',
        r'\bProf\.\s': 'Professor ',
        r'\betc\.\b':  'et cetera',
        r'\bvs\.\b':   'versus',
        r'\be\.g\.\b': 'for example',
        r'\bi\.e\.\b': 'that is',
    }
    for pattern, replacement in abbrevs.items():
        text = re.sub(pattern, replacement, text)

    # Ellipses → explicit pause punctuation (Kokoro reads "..." as a pause)
    # Normalize various ellipsis forms to a standard three-dot with spaces
    text = re.sub(r'\.{2,}', ' ... ', text)
    text = re.sub(r'\u2026', ' ... ', text)  # Unicode ellipsis character

    # Insert a brief comma-pause: after sentence-internal commas add a short rest
    # We use a comma followed by a narrow space + comma trick recognised by Kokoro
    # as a micro-pause without altering semantics.
    # (Kokoro tends to rush past commas; the duplicate-comma trick nudges pacing.)
    text = re.sub(r',\s+', ', , ', text)

    # Clean up any doubled spaces introduced above
    text = re.sub(r'  +', ' ', text)

    return text.strip()


# ---------------------------------------------------------------------------
# AUDIO POST-PROCESSING
# ---------------------------------------------------------------------------

def apply_highpass_filter(samples: np.ndarray, sr: int, cutoff_hz: float) -> np.ndarray:
    """Simple first-order high-pass IIR filter to remove low-end muddiness."""
    rc = 1.0 / (2.0 * np.pi * cutoff_hz)
    dt = 1.0 / sr
    alpha = rc / (rc + dt)
    filtered = np.zeros_like(samples)
    filtered[0] = samples[0]
    for i in range(1, len(samples)):
        filtered[i] = alpha * (filtered[i - 1] + samples[i] - samples[i - 1])
    return filtered


def apply_presence_boost(samples: np.ndarray, sr: int,
                         low_hz: float = 3000.0, high_hz: float = 6000.0,
                         gain_db: float = PRESENCE_GAIN_DB) -> np.ndarray:
    """Gentle +2dB presence boost in the 3kHz-6kHz clarity band.

    Isolates the clarity band with two first-order IIR filters (band-pass),
    scales the band by the linear gain, then mixes back with the dry signal.
    Enhances consonant definition and the crisp, 'processed' JARVIS quality.
    """
    gain_linear = 10.0 ** (gain_db / 20.0) - 1.0  # additive gain for the band

    # High-pass at low_hz to extract 'above 3kHz' component
    rc_lo = 1.0 / (2.0 * np.pi * low_hz)
    dt = 1.0 / sr
    alpha_lo = rc_lo / (rc_lo + dt)
    hp_lo = np.zeros_like(samples)
    hp_lo[0] = samples[0]
    for i in range(1, len(samples)):
        hp_lo[i] = alpha_lo * (hp_lo[i - 1] + samples[i] - samples[i - 1])

    # Low-pass at high_hz to cap at 6kHz (first-order RC)
    alpha_hi = dt / (dt + 1.0 / (2.0 * np.pi * high_hz))
    lp_hi = np.zeros_like(hp_lo)
    lp_hi[0] = hp_lo[0]
    for i in range(1, len(hp_lo)):
        lp_hi[i] = lp_hi[i - 1] + alpha_hi * (hp_lo[i] - lp_hi[i - 1])

    # Mix: dry + gain_linear * band
    return (samples + gain_linear * lp_hi).astype(np.float32)


def apply_reverb(samples: np.ndarray, sr: int,
                 decay_sec: float = REVERB_DECAY,
                 wet_mix: float = REVERB_MIX) -> np.ndarray:
    """Very short room-simulation reverb via a comb-filter approach.

    Creates a barely-perceptible spatial shimmer — the 'clean processed'
    quality that distinguishes the film JARVIS voice from bare TTS output.
    """
    delay_samples = int(sr * decay_sec)
    if delay_samples < 1:
        return samples
    # Build a simple FIR impulse for a single early reflection
    impulse = np.zeros(delay_samples + 1)
    impulse[0] = 1.0
    impulse[-1] = wet_mix * 0.5
    # Convolve and trim to original length
    reverbed = np.convolve(samples, impulse)[:len(samples)]
    return reverbed.astype(np.float32)


def normalize_to_peak(samples: np.ndarray, target_dbfs: float = PEAK_TARGET) -> np.ndarray:
    """Normalize audio so the peak amplitude equals target_dbfs."""
    peak = np.max(np.abs(samples))
    if peak == 0:
        return samples
    target_linear = 10.0 ** (target_dbfs / 20.0)
    return (samples * (target_linear / peak)).astype(np.float32)


def apply_soft_limiter(samples: np.ndarray, threshold: float = 0.95) -> np.ndarray:
    """Soft knee limiter to prevent clipping after processing chain."""
    # tanh-based soft clipping above threshold
    above = np.abs(samples) > threshold
    sign = np.sign(samples)
    over = np.abs(samples) - threshold
    samples[above] = sign[above] * (threshold + np.tanh(over[above]) * (1.0 - threshold))
    return samples


def apply_pydub_compression(audio_path: str) -> None:
    """Apply a very light dynamic compression using pydub for consistent volume.

    Compression ratio 2:1 with gentle attack/release — evens out any loud
    consonant bursts without squashing the natural dynamics of speech.
    """
    try:
        from pydub import AudioSegment
        from pydub.effects import compress_dynamic_range
        seg = AudioSegment.from_wav(audio_path)
        # Gentle compression: threshold -18dBFS, ratio 2.0, 10ms attack, 200ms release
        compressed = compress_dynamic_range(
            seg,
            threshold=-18.0,
            ratio=2.0,
            attack=10.0,
            release=200.0
        )
        compressed.export(audio_path, format='wav')
    except Exception:
        pass  # Compression is cosmetic — don't fail if pydub lacks the effect


def polish_audio(audio: np.ndarray, sr: int) -> np.ndarray:
    """Full post-processing chain: highpass → presence boost → reverb → normalize → limit."""
    # 1. High-pass filter: remove sub-150Hz rumble (tighter than before)
    audio = apply_highpass_filter(audio, sr, HIGHPASS_HZ)
    # 2. Presence boost: gentle +2dB shelf in the 3kHz-6kHz clarity band
    audio = apply_presence_boost(audio, sr)
    # 3. Subtle reverb for spatial depth (6% wet — tighter than before)
    audio = apply_reverb(audio, sr, REVERB_DECAY, REVERB_MIX)
    # 4. Soft limiter before normalization
    audio = apply_soft_limiter(audio)
    # 5. Normalize to target peak
    audio = normalize_to_peak(audio, PEAK_TARGET)
    return audio


# ---------------------------------------------------------------------------
# SAVE & EXPORT
# ---------------------------------------------------------------------------

def save_mp3(audio_array: np.ndarray, sample_rate: int, output_path: str) -> str:
    """Save polished audio to 192kbps MP3 (via lameenc — pure Python, no ffmpeg needed)."""
    wav_path = output_path.replace('.mp3', '_tmp.wav')
    sf.write(wav_path, audio_array, sample_rate)

    # Use lameenc directly — avoids ffmpeg/pydub dependency issues
    import wave
    import lameenc
    with wave.open(wav_path, 'rb') as wf:
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        sr = wf.getframerate()
        ch = wf.getnchannels()

    enc = lameenc.Encoder()
    enc.set_bit_rate(192)
    enc.set_in_sample_rate(sr)
    enc.set_channels(ch)
    enc.set_quality(2)

    with open(output_path, 'wb') as f:
        f.write(enc.encode(pcm.tobytes()) + enc.flush())

    os.remove(wav_path)
    return output_path


# ---------------------------------------------------------------------------
# MAIN GENERATION
# ---------------------------------------------------------------------------

def generate_jarvis_speech(text: str, output_path: str | None = None) -> str:
    """Generate polished JARVIS-style speech. Returns the output filepath."""
    import warnings
    warnings.filterwarnings('ignore')

    from kokoro import KPipeline

    # Preprocess text for natural pacing
    processed_text = preprocess_text(text)

    pipeline = KPipeline(lang_code=JARVIS_LANG, repo_id='hexgrad/Kokoro-82M')

    segments = []
    for result in pipeline(processed_text, voice=JARVIS_VOICE, speed=JARVIS_SPEED):
        segments.append(result.audio)

    if not segments:
        raise RuntimeError("Kokoro returned no audio segments")

    audio = np.concatenate(segments).astype(np.float32)

    # Apply full post-processing chain
    audio = polish_audio(audio, SAMPLE_RATE)

    if output_path is None:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(WORKSPACE, f'jarvis_{ts}.mp3')

    return save_mp3(audio, SAMPLE_RATE, output_path)


def main():
    # Read text from argv[1] or stdin
    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        print("Usage: python3 jarvis_tts.py \"Your text here\"", file=sys.stderr)
        print("       echo \"Your text\" | python3 jarvis_tts.py", file=sys.stderr)
        sys.exit(1)

    if not text:
        print("ERROR: Empty text provided", file=sys.stderr)
        sys.exit(1)

    output_path = generate_jarvis_speech(text)
    size = os.path.getsize(output_path)

    # Print the path for Hermes to pick up as MEDIA:
    print(output_path)

    # Also print size to stderr for diagnostics
    print(f"[JARVIS TTS] Generated {size:,} bytes → {output_path}", file=sys.stderr)


if __name__ == '__main__':
    main()
