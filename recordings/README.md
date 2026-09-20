# Recordings

Audio files are kept **locally only** and excluded from git (see `.gitignore`). This directory tracks only structured notes and metadata for each session.

## Why Local Only?

Audio files are large. Git is not designed for binary files of that size. Keep your `.wav`/`.mp3` files in a local folder (or a cloud drive like Dropbox or Google Drive) and use this directory for written notes that git *can* version effectively.

## Directory Structure

```
recordings/
├── README.md
├── template-notes.md
└── sessions/
    └── YYYY-MM-DD/
        └── notes.md
```

## Naming Convention

Match the recording date to the journal log date. If you logged `journal/logs/2026-03-26.md`, your recording notes live in `recordings/sessions/2026-03-26/notes.md`. This makes cross-referencing effortless.

## Suggested Local File Naming

For the actual audio files on your drive, use:
```
YYYY-MM-DD_exercise-name_take-N.wav
```
Example: `2026-03-26_diaphragm-breathing_take-2.wav`

## Listening Back

Listening to recordings is more useful than you expect. Things to notice:
- Are consonants clear?
- Is pitch steady or wavering?
- Does the voice sound strained or relaxed?
- Does volume drop at phrase ends?
- Is there tension in the tone quality?
