# SoundKit — Static Website

## Folder Structure

```
soundkit/
├── index.html        ← Landing page
├── library.html      ← Song library + download page
├── songs.csv         ← Auto-managed song database
├── scan_songs.py     ← Python scanner script
└── audio/            ← PUT YOUR .mp3 FILES HERE
    ├── Midnight Drip - Trap.mp3
    ├── Cold Rain - Lo-Fi.mp3
    └── ...
```

## Naming Convention for Audio Files

Files must follow this format exactly:

```
Song Name - Genre.mp3
```

Examples:
- `Midnight Drip - Trap.mp3`
- `Cold Rain - Lo-Fi.mp3`
- `Glass City - Ambient.mp3`

The part before ` - ` becomes the track name.  
The part after ` - ` becomes the genre tag.

---

## Running the Scanner

```bash
# Install mutagen for duration detection (recommended)
pip install mutagen

# Run the scanner
python scan_songs.py
```

The scanner will:
- Find all audio files in the same directory
- Parse name and genre from the filename
- Get the track duration (if mutagen is installed)
- Add new entries to `songs.csv`
- **Never modify existing entries in the CSV**

---

## Serving the Site

Since the library page reads `songs.csv` via `fetch()`, you need a local server:

```bash
# Python
python -m http.server 8080

# Node (npx)
npx serve .
```

Then open `http://localhost:8080`.

To host publicly, upload the whole folder to GitHub Pages, Netlify, or any static host.

---

## Downloads

Each track downloads with the filename:  
`Song Name - SoundKit.mp3`

The "Download All" button downloads every visible track (respects active genre filter).
