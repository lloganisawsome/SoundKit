#!/usr/bin/env python3
"""
SoundKit Song Scanner
---------------------
Scans the script's directory for audio files named "Song Name - Genre.mp3",
extracts metadata, and appends new entries to songs.csv.
Existing entries in the CSV are NEVER modified.

Usage:
    python scan_songs.py
"""

import os
import csv
import sys
from datetime import date
from pathlib import Path

try:
    from mutagen.mp3 import MP3
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

# ── CONFIG ────────────────────────────────────────────────────────────────────
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a"}
CSV_FILE = "songs.csv"
CSV_HEADERS = ["name", "genre", "duration", "date_added"]

# ── HELPERS ───────────────────────────────────────────────────────────────────

def format_duration(seconds: float) -> str:
    """Convert seconds to M:SS format."""
    total = int(round(seconds))
    m, s = divmod(total, 60)
    return f"{m}:{s:02d}"


def get_audio_duration(filepath: Path) -> str:
    """Return duration string for an audio file. Falls back to '0:00'."""
    if not MUTAGEN_AVAILABLE:
        return "0:00"
    try:
        ext = filepath.suffix.lower()
        if ext == ".mp3":
            audio = MP3(str(filepath))
            return format_duration(audio.info.length)
        # For other formats mutagen can still work via generic File
        from mutagen import File as MutagenFile
        audio = MutagenFile(str(filepath))
        if audio and audio.info:
            return format_duration(audio.info.length)
    except Exception:
        pass
    return "0:00"


def parse_filename(filename: str):
    """
    Parse a filename like  "Song Name - Genre.mp3"
    into (name, genre). Returns None if format doesn't match.
    """
    stem = Path(filename).stem  # strip extension
    if " - " not in stem:
        return None
    # Split only on the LAST " - " to handle names containing " - "
    parts = stem.rsplit(" - ", 1)
    name  = parts[0].strip()
    genre = parts[1].strip()
    if not name or not genre:
        return None
    return name, genre


def load_csv(csv_path: Path) -> dict:
    """
    Load existing CSV into a dict keyed by lowercase (name, genre) tuple.
    Returns {(name_lower, genre_lower): row_dict, ...}
    """
    existing = {}
    if not csv_path.exists():
        return existing

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["name"].strip().lower(), row["genre"].strip().lower())
            existing[key] = row

    return existing


def scan_audio_files(directory: Path) -> list:
    """Return a list of audio Path objects in the given directory (non-recursive)."""
    files = []
    for entry in sorted(directory.iterdir()):
        if entry.is_file() and entry.suffix.lower() in AUDIO_EXTENSIONS:
            files.append(entry)
    return files


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    script_dir = Path(__file__).parent.resolve()
    csv_path   = script_dir / CSV_FILE
    today      = date.today().isoformat()

    print(f"\n{'='*56}")
    print(f"  SoundKit Song Scanner")
    print(f"  Directory : {script_dir}")
    print(f"  CSV file  : {csv_path.name}")
    print(f"{'='*56}\n")

    if not MUTAGEN_AVAILABLE:
        print("  ⚠  mutagen not found — install it for duration detection:")
        print("     pip install mutagen\n")
        print("  Continuing with duration = '0:00' …\n")

    # Load what we already know
    existing = load_csv(csv_path)
    print(f"  Existing entries in CSV : {len(existing)}")

    # Scan for audio files
    audio_files = scan_audio_files(script_dir)
    print(f"  Audio files found       : {len(audio_files)}\n")

    new_rows  = []
    skipped   = 0
    bad_names = []

    for filepath in audio_files:
        parsed = parse_filename(filepath.name)
        if parsed is None:
            bad_names.append(filepath.name)
            continue

        name, genre = parsed
        key = (name.lower(), genre.lower())

        if key in existing:
            print(f"  ✓ (skip)  {name} — already in CSV")
            skipped += 1
            continue

        # New song — get duration and add
        duration = get_audio_duration(filepath)
        row = {
            "name"      : name,
            "genre"     : genre,
            "duration"  : duration,
            "date_added": today,
        }
        new_rows.append(row)
        print(f"  + (add)   {name} [{genre}]  {duration}")

    # Write back CSV
    if new_rows:
        file_exists = csv_path.exists()
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            if not file_exists or csv_path.stat().st_size == 0:
                writer.writeheader()
            writer.writerows(new_rows)
        print(f"\n  ✅  Added {len(new_rows)} new track(s) to {CSV_FILE}")
    else:
        print(f"\n  ℹ  No new tracks to add.")

    if skipped:
        print(f"  ⏭  Skipped {skipped} existing track(s).")

    if bad_names:
        print(f"\n  ⚠  {len(bad_names)} file(s) skipped — wrong naming format:")
        print("     Expected:  Song Name - Genre.mp3")
        for n in bad_names:
            print(f"     • {n}")

    # ── ENSURE HEADER EXISTS if CSV is brand-new ──────────────────────────────
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
        print(f"\n  📄  Created empty {CSV_FILE} (no audio files found yet).")

    print(f"\n{'='*56}\n")


if __name__ == "__main__":
    main()
