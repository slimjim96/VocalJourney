"""
analyze_pitch.py

Analyzes pitch over time in a vocal recording.
Outputs a summary and a PNG plot showing pitch drift and accuracy.

Usage:
    python analyze_pitch.py <audio_file.wav> [--target NOTE]

Examples:
    python analyze_pitch.py recording.wav
    python analyze_pitch.py recording.wav --target C4
    python analyze_pitch.py recording.wav --target A3 --threshold 25
"""

import argparse
import sys
from pathlib import Path

import librosa
import matplotlib.pyplot as plt
import numpy as np


NOTE_FREQUENCIES = {
    "C2": 65.41, "D2": 73.42, "E2": 82.41, "F2": 87.31, "G2": 98.00,
    "A2": 110.00, "B2": 123.47,
    "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.00,
    "A3": 220.00, "B3": 246.94,
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.00,
    "A4": 440.00, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46, "G5": 783.99,
    "A5": 880.00, "B5": 987.77,
}


def hz_to_note(freq_hz: float) -> str:
    """Convert a frequency in Hz to the nearest note name."""
    if freq_hz <= 0:
        return "—"
    semitones = 12 * np.log2(freq_hz / 440.0)
    note_index = int(round(semitones)) + 57  # A4 = index 57
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = note_index // 12
    note = notes[note_index % 12]
    return f"{note}{octave}"


def cents_from_target(freq_hz: float, target_hz: float) -> float:
    """Return cents deviation from a target frequency (positive = sharp, negative = flat)."""
    if freq_hz <= 0 or target_hz <= 0:
        return float("nan")
    return 1200 * np.log2(freq_hz / target_hz)


def analyze_pitch(audio_path: Path, target_note: str | None, threshold_cents: int) -> None:
    print(f"\nLoading: {audio_path}")
    y, sr = librosa.load(str(audio_path), sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"Duration: {duration:.1f}s  |  Sample rate: {sr} Hz")

    # Extract pitch using pyin (more accurate than yin for vocals)
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C6"),
        sr=sr,
    )

    times = librosa.times_like(f0, sr=sr)
    voiced_f0 = f0[voiced_flag]

    if len(voiced_f0) == 0:
        print("No voiced frames detected. Is this a vocal recording?")
        sys.exit(1)

    median_pitch = float(np.nanmedian(voiced_f0))
    mean_pitch = float(np.nanmean(voiced_f0))
    voiced_pct = (voiced_flag.sum() / len(voiced_flag)) * 100

    print(f"\n--- Pitch Analysis ---")
    print(f"Median pitch:  {median_pitch:.1f} Hz  ({hz_to_note(median_pitch)})")
    print(f"Mean pitch:    {mean_pitch:.1f} Hz  ({hz_to_note(mean_pitch)})")
    print(f"Voiced frames: {voiced_pct:.1f}%")

    target_hz = None
    if target_note:
        target_note_upper = target_note.upper()
        if target_note_upper not in NOTE_FREQUENCIES:
            print(f"Unknown note '{target_note}'. Valid examples: C3, A4, G2")
            sys.exit(1)
        target_hz = NOTE_FREQUENCIES[target_note_upper]
        cents_vals = np.array([
            cents_from_target(f, target_hz)
            for f in voiced_f0
            if not np.isnan(f)
        ])
        in_tune_pct = float(np.mean(np.abs(cents_vals) <= threshold_cents) * 100)
        avg_deviation = float(np.nanmean(np.abs(cents_vals)))
        print(f"\nTarget note:   {target_note_upper} ({target_hz:.1f} Hz)")
        print(f"Threshold:     ±{threshold_cents} cents")
        print(f"In tune:       {in_tune_pct:.1f}%")
        print(f"Avg deviation: {avg_deviation:.1f} cents")
        if avg_deviation < 15:
            print("Assessment:    Excellent pitch accuracy")
        elif avg_deviation < 30:
            print("Assessment:    Good — minor drift, keep working on ear-to-voice feedback")
        elif avg_deviation < 50:
            print("Assessment:    Fair — noticeable drift, focus on pitch matching exercises")
        else:
            print("Assessment:    Needs work — significant pitch drift, slow down and use a tuner")

    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    fig.suptitle(f"Pitch Analysis — {audio_path.name}", fontsize=13)

    ax1 = axes[0]
    ax1.plot(times, f0, color="steelblue", linewidth=0.8, label="Detected pitch")
    if target_hz:
        ax1.axhline(y=target_hz, color="green", linestyle="--", linewidth=1, label=f"Target: {target_note_upper}")
        upper = target_hz * 2 ** (threshold_cents / 1200)
        lower = target_hz * 2 ** (-threshold_cents / 1200)
        ax1.fill_between(times, lower, upper, alpha=0.15, color="green", label=f"±{threshold_cents} cent range")
    ax1.set_ylabel("Frequency (Hz)")
    ax1.set_ylim(50, 1000)
    ax1.legend(loc="upper right", fontsize=8)
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    ax2.fill_between(times, voiced_probs, alpha=0.6, color="darkorange", label="Voiced probability")
    ax2.set_ylabel("Voiced Probability")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylim(0, 1)
    ax2.legend(loc="upper right", fontsize=8)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = audio_path.with_name(audio_path.stem + "_pitch.png")
    plt.savefig(out_path, dpi=150)
    print(f"\nPlot saved: {out_path}")
    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze pitch in a vocal recording.")
    parser.add_argument("audio", type=Path, help="Path to .wav file")
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Target note to measure accuracy against (e.g. C4, A3)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=25,
        help="In-tune threshold in cents (default: 25)",
    )
    args = parser.parse_args()

    if not args.audio.exists():
        print(f"File not found: {args.audio}")
        sys.exit(1)

    analyze_pitch(args.audio, args.target, args.threshold)


if __name__ == "__main__":
    main()
