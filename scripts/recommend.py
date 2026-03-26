"""
recommend.py

Reads a journal log and recommends exercises based on what you struggled with.
Scans for struggle keywords and maps them to specific exercise files.

Usage:
    python recommend.py                        # uses most recent log in ../journal/logs/
    python recommend.py path/to/log.md         # specify a log file
"""

import argparse
import re
import sys
from pathlib import Path


EXERCISE_MAP = [
    {
        "keywords": [
            "breath", "breathing", "air", "running out", "out of air",
            "shallow", "diaphragm", "exhale", "inhale",
        ],
        "exercise": "exercises/projection/diaphragm-breathing.md",
        "reason": "Breath support issues detected",
    },
    {
        "keywords": [
            "resonance", "thin", "weak", "no carry", "projection", "throat",
            "nasal", "buzz", "placement", "forward",
        ],
        "exercise": "exercises/projection/resonance-placement.md",
        "reason": "Resonance or projection issues detected",
    },
    {
        "keywords": [
            "articulation", "clarity", "mumble", "unclear", "consonant",
            "diction", "muddy", "hard to understand",
        ],
        "exercise": "exercises/projection/consonant-articulation.md",
        "reason": "Articulation or clarity issues detected",
    },
    {
        "keywords": [
            "pitch", "flat", "sharp", "out of tune", "off key", "tuner",
            "off pitch", "hit the note", "wrong note", "interval",
        ],
        "exercise": "exercises/singing/pitch-matching.md",
        "reason": "Pitch accuracy issues detected",
    },
    {
        "keywords": [
            "warm up", "cold", "range", "high notes", "low notes",
            "scale", "arpeggio", "register", "break",
        ],
        "exercise": "exercises/singing/scales-and-arpeggios.md",
        "reason": "Range or warm-up issues detected",
    },
    {
        "keywords": [
            "sustain", "sustaining", "long note", "phrase", "phrase end",
            "drop off", "running out", "held note", "support",
        ],
        "exercise": "exercises/singing/breath-control.md",
        "reason": "Breath control or phrase sustain issues detected",
    },
    {
        "keywords": [
            "vibrato", "wobble", "tremor", "oscillation", "straight tone",
            "forced", "uncontrolled vibrato",
        ],
        "exercise": "exercises/singing/vibrato-foundation.md",
        "reason": "Vibrato issues detected",
    },
]


def find_latest_log(logs_dir: Path) -> Path | None:
    logs = sorted(logs_dir.glob("*.md"), reverse=True)
    return logs[0] if logs else None


def extract_struggle_sections(text: str) -> str:
    """Extract lines from 'What Was Hard' and 'Focus for Next Session' sections."""
    pattern = re.compile(
        r"##\s*(What Was Hard|Focus for Next Session)(.*?)(?=##|\Z)",
        re.DOTALL | re.IGNORECASE,
    )
    sections = pattern.findall(text)
    return " ".join(content for _, content in sections).lower()


def recommend(log_path: Path) -> None:
    text = log_path.read_text(encoding="utf-8")
    struggle_text = extract_struggle_sections(text)
    full_text = text.lower()

    print(f"\nAnalyzing: {log_path.name}")
    print(f"{'─' * 50}")

    recommendations = []
    for entry in EXERCISE_MAP:
        matched_keywords = [kw for kw in entry["keywords"] if kw in struggle_text]
        if not matched_keywords:
            # Fall back to scanning the full log
            matched_keywords = [kw for kw in entry["keywords"] if kw in full_text]

        if matched_keywords:
            recommendations.append({
                "exercise": entry["exercise"],
                "reason": entry["reason"],
                "matched": matched_keywords[:3],
            })

    if not recommendations:
        print("\nNo specific struggles detected in this log.")
        print("Recommended: Follow the default weekly schedule in exercises/README.md")
        return

    print(f"\nRecommended exercises for your next session:\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['exercise']}")
        print(f"     Reason: {rec['reason']}")
        print(f"     Keywords matched: {', '.join(rec['matched'])}")
        print()

    print("Suggested session plan:")
    print("  1. Always start with: exercises/projection/diaphragm-breathing.md (5 min)")
    for rec in recommendations[:2]:
        print(f"  2. Then: {rec['exercise']} (10–15 min)")
    print("  3. Record at least one take and fill out recordings/template-notes.md")
    print("  4. Log the session in journal/logs/ using journal/template.md")


def main() -> None:
    parser = argparse.ArgumentParser(description="Get exercise recommendations from a journal log.")
    parser.add_argument(
        "log",
        type=Path,
        nargs="?",
        default=None,
        help="Path to journal log .md file (default: most recent in ../journal/logs/)",
    )
    args = parser.parse_args()

    if args.log:
        log_path = args.log
        if not log_path.exists():
            print(f"File not found: {log_path}")
            sys.exit(1)
    else:
        logs_dir = Path(__file__).parent.parent / "journal" / "logs"
        log_path = find_latest_log(logs_dir)
        if not log_path:
            print(f"No log files found in {logs_dir}")
            print("Create a session log using journal/template.md first.")
            sys.exit(1)
        print(f"Using most recent log: {log_path.name}")

    recommend(log_path)


if __name__ == "__main__":
    main()
