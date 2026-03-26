"""
analyze_volume.py

Analyzes volume (dB RMS) over time in a vocal recording.
Reports dynamic range, consistency, and projected vs. thin segments.

Usage:
    python analyze_volume.py <audio_file.wav>

Example:
    python analyze_volume.py recording.wav
"""

import argparse
import sys
from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np


def analyze_volume(audio_path: Path) -> None:
    print(f"\nLoading: {audio_path}")
    y, sr = librosa.load(str(audio_path), sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"Duration: {duration:.1f}s  |  Sample rate: {sr} Hz")

    # RMS energy per frame
    frame_length = 2048
    hop_length = 512
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    # Convert to dB, clip floor at -60 dB
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    rms_db = np.maximum(rms_db, -60.0)

    # Stats (exclude silence below -40 dB)
    active_mask = rms_db > -40.0
    if active_mask.sum() == 0:
        print("No active vocal frames detected. Check the recording.")
        sys.exit(1)

    active_db = rms_db[active_mask]
    avg_db = float(np.mean(active_db))
    peak_db = float(np.max(rms_db))
    floor_db = float(np.min(active_db))
    dynamic_range = peak_db - floor_db
    std_db = float(np.std(active_db))

    print(f"\n--- Volume Analysis ---")
    print(f"Average level:  {avg_db:.1f} dB (relative to peak)")
    print(f"Peak level:     {peak_db:.1f} dB")
    print(f"Active floor:   {floor_db:.1f} dB")
    print(f"Dynamic range:  {dynamic_range:.1f} dB")
    print(f"Std deviation:  {std_db:.1f} dB  (lower = more consistent)")

    # Drop-off detection: segments where level falls more than 10 dB below average
    dropoff_mask = active_mask & (rms_db < avg_db - 10)
    dropoff_pct = float(dropoff_mask.sum() / active_mask.sum() * 100)
    print(f"Volume drop-offs (>10 dB below avg): {dropoff_pct:.1f}% of voiced time")

    # Assessment
    print(f"\n--- Assessment ---")
    if std_db < 4:
        print("Consistency:  Excellent — very even volume throughout")
    elif std_db < 8:
        print("Consistency:  Good — some variation, but controlled")
    elif std_db < 14:
        print("Consistency:  Fair — noticeable fluctuations, work on breath support")
    else:
        print("Consistency:  Needs work — high volume variance, focus on diaphragm control")

    if dropoff_pct > 20:
        print("Projection:   Volume drops significantly at phrase ends — support through the full phrase")
    elif dropoff_pct > 10:
        print("Projection:   Some drop-off at phrase ends — keep breath engaged to the last note")
    else:
        print("Projection:   Good phrase-end support")

    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    fig.suptitle(f"Volume Analysis — {audio_path.name}", fontsize=13)

    ax1 = axes[0]
    ax1.plot(times, rms_db, color="steelblue", linewidth=0.8, label="RMS level (dB)")
    ax1.axhline(y=avg_db, color="green", linestyle="--", linewidth=1, label=f"Avg: {avg_db:.1f} dB")
    ax1.axhline(y=avg_db - 10, color="orange", linestyle=":", linewidth=1, label="Drop-off threshold")
    ax1.set_ylabel("Level (dB, relative to peak)")
    ax1.set_ylim(-65, 5)
    ax1.legend(loc="lower right", fontsize=8)
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    waveform_times = np.linspace(0, duration, len(y))
    ax2.fill_between(waveform_times, y, alpha=0.5, color="darkorange")
    ax2.set_ylabel("Amplitude")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylim(-1, 1)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = audio_path.with_name(audio_path.stem + "_volume.png")
    plt.savefig(out_path, dpi=150)
    print(f"\nPlot saved: {out_path}")
    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze volume in a vocal recording.")
    parser.add_argument("audio", type=Path, help="Path to .wav file")
    args = parser.parse_args()

    if not args.audio.exists():
        print(f"File not found: {args.audio}")
        sys.exit(1)

    analyze_volume(args.audio)


if __name__ == "__main__":
    main()
