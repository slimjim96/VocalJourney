# Scripts

Python tools for objective feedback on your recordings. Each script does one thing.

## Setup

```bash
cd scripts/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Scripts

### `analyze_pitch.py`
Reads a `.wav` file, extracts pitch over time, and generates a plot showing pitch drift and accuracy.

```bash
python analyze_pitch.py ../recordings/sessions/2026-03-26/my-recording.wav --target C4
```

Outputs:
- Terminal summary: average pitch, variance, % of time in tune
- PNG plot saved alongside the input file

### `analyze_volume.py`
Measures decibel levels across a recording to assess dynamic range and consistency.

```bash
python analyze_volume.py ../recordings/sessions/2026-03-26/my-recording.wav
```

Outputs:
- Terminal: average dB, peak dB, floor dB, dynamic range
- PNG waveform plot with dB levels

### `recommend.py`
Reads your most recent journal log, scans for struggle keywords, and maps them to specific exercises.

```bash
python recommend.py
# or specify a log file:
python recommend.py ../journal/logs/2026-03-26.md
```

Outputs:
- List of recommended exercises based on what you logged struggling with
- Suggested session plan for your next practice

## Input Format

All audio scripts expect `.wav` files. To convert from other formats:
```bash
# Using ffmpeg (install separately)
ffmpeg -i recording.mp3 recording.wav
ffmpeg -i recording.m4a recording.wav
```

## Dependencies

See `requirements.txt`. Core libraries: `librosa`, `numpy`, `matplotlib`.
