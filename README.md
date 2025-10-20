# findPublicMedia

A project to find and manage public media resources.

## 🩵 Step 1 — The Tiny Spark

Goal: Search for a movie and open a legal link in your browser.

### 1) Get a free TMDB API key
- Create an account at https://www.themoviedb.org/
- Go to your account settings → API → Request an API key (v3)
- Copy the key

In your terminal (zsh), set it for this session:

```zsh
export TMDB_API_KEY="YOUR_TMDB_V3_API_KEY"
```

Optional: add that line to your `~/.zshrc` to persist it across sessions.

### 2) Run the tiny app
From the repo root in VS Code’s terminal:

```zsh
python3 vibe_streamer.py
```

When prompted, type:

```
Night of the Living Dead
```

It will open an Archive.org search page for that film in your default browser.

Tip: you can also run without a key (it will still open an Archive.org search by raw title),
but the TMDB key improves title/year matching.

## 🧩 Step 2 — Subtitles (Optional)

Add a function to retrieve a subtitle link from OpenSubtitles.

### 1) Optional: OpenSubtitles API key
You can use the public site without a key, or provide an API key for better results.

```zsh
export OPENSUBTITLES_API_KEY="YOUR_OS_API_KEY"
```

### 2) Run with a language code
Default language is English (`en`). You can change it, for example Spanish (`es`):

```zsh
python3 vibe_streamer.py --no-open --subs-lang es "Night of the Living Dead"
```

You will see two links printed:
- Archive.org search URL
- OpenSubtitles URL (direct API result if key provided; otherwise a site search link)

---

## 🎬 Streaming Feature — Instant Playback

**NEW!** Stream movies from Archive.org directly, no downloads required!

### Quick Start

Search for a movie and stream it instantly:

```zsh
python3 vibe_streamer.py "His Girl Friday" --stream
```

This will:
1. Search TMDB for the movie
2. Find a matching Archive.org item
3. Launch VLC with the movie and subtitles loaded

### Streaming Modes

**Option 1: Integrated Search + Stream**
```zsh
# Search and play in one command
python3 vibe_streamer.py "Charade" --stream

# Search and mount for Plex
python3 vibe_streamer.py "Night of the Living Dead" --plex
```

**Option 2: Direct Stream (if you know the Archive.org link)**
```zsh
# Quick play in VLC
python3 stream_now.py --ia-link "https://archive.org/details/HisGirlFriday1940" --mode quick

# Mount for Plex/Jellyfin
python3 stream_now.py --ia-link "https://archive.org/details/HisGirlFriday1940" --mode plex
```

### Prerequisites

**For Quick Play mode (VLC):**
- VLC media player
  ```zsh
  brew install --cask vlc  # macOS
  # or: sudo apt install vlc  # Linux
  ```

**For Plex mode (rclone mount):**
- rclone
  ```zsh
  brew install rclone  # macOS
  # or: curl https://rclone.org/install.sh | sudo bash  # Linux
  ```
- Optional: pysubs2 for subtitle conversion
  ```zsh
  pip install pysubs2
  ```

### Quick Play Mode

Instantly play a movie with subtitles in VLC:

```zsh
python3 stream_now.py --ia-link "https://archive.org/details/HisGirlFriday1940" --mode quick
```

This will:
1. Fetch Archive.org metadata
2. Find the best video file (.mp4/.ogv)
3. Find matching subtitles (.srt/.vtt)
4. Launch VLC with both loaded

### Plex/Jellyfin Mode

Mount an Archive.org item as a local folder for streaming through Plex:

```zsh
python3 stream_now.py --ia-link "https://archive.org/details/HisGirlFriday1940" --mode plex
```

This will:
1. Set up rclone HTTP remote
2. Mount the item to `~/ArchiveMount/<identifier>`
3. Print instructions to add the folder to Plex/Jellyfin

### Managing Mounts

Use the helper script to manage your Archive.org mounts:

```zsh
# List all active mounts
python3 mount_archive.py list

# Unmount a specific item
python3 mount_archive.py unmount HisGirlFriday1940

# Unmount all items
python3 mount_archive.py unmount-all
```

### Examples

**Classic films available on Archive.org:**
```zsh
# Night of the Living Dead (1968)
python3 stream_now.py --ia-link "https://archive.org/details/night_of_the_living_dead" --mode quick

# His Girl Friday (1940)
python3 stream_now.py --ia-link "https://archive.org/details/HisGirlFriday1940" --mode quick

# Charade (1963)
python3 stream_now.py --ia-link "https://archive.org/details/Charade_201712" --mode plex
```

## 🤖 AI-Powered Batch Mount

**NEW!** Describe what you want to watch and automatically mount multiple movies at once!

### Quick Start

```zsh
# Interactive mode - just run it and describe what you want
python3 ai_mount_list.py

# Or provide the prompt directly
python3 ai_mount_list.py --prompt "classic film noir from the 1940s"

# Limit the number of results
python3 ai_mount_list.py --prompt "sci-fi movies about AI" --limit 10

# Skip confirmation prompt
python3 ai_mount_list.py --prompt "hitchcock thrillers" --yes
```

### How It Works

1. **Describe your mood**: Use natural language like:
   - "classic film noir from the 1940s"
   - "sci-fi movies about artificial intelligence"
   - "comedies from the silent era"
   - "hitchcock psychological thrillers"

2. **AI finds matches**: Searches TMDB and Archive.org using your description

3. **Organized collections**: Creates a descriptive subfolder for each search query
   - `~/ArchiveMount/classic_film_noir_1940s/`
   - `~/ArchiveMount/hitchcock_psychological_thrillers/`
   - `~/ArchiveMount/silent_comedies_charlie_chaplin/`

4. **Auto-mount**: Mounts up to 20 movies in the collection folder

5. **Add to Plex**: Point your Plex library at the collection folder and scan

### Example Session

```zsh
$ python3 ai_mount_list.py

============================================================
🎬  AI-POWERED MOVIE MOUNT LIST CREATOR  🎬
============================================================

📝 Describe the movies you're looking for:
   Examples:
   - 'classic film noir from the 1940s'
   - 'sci-fi movies about artificial intelligence'

Your description: classic film noir from the 1940s

🔍 Searching for movies matching: 'classic film noir from the 1940s'...

✨ Found 5 movies:

#    Title                     Year   Identifier
1    The Stranger              1946   TheStranger_0
2    Scarlet Street            1945   ScarletStreet
3    The Hitch-Hiker           1953   Hitch_Hiker
4    The Chase                 1946   TheChase_
5    His Girl Friday           1940   his_girl_friday

🚀 Mount all 5 movies? (y/n): y

[1/5] 🎬 Mounting: The Stranger
      ✅ Successfully mounted

📊 MOUNT SUMMARY
Total movies:     5
✅ Mounted:       5

🎉 Successfully mounted movies are ready for Plex/Jellyfin!
```

### Options

```zsh
--prompt "text"       # Natural language movie description
--limit N             # Max number of movies to find (default: 20)
--mount-base PATH     # Base directory for mounts (default: ~/ArchiveMount)
--yes, -y             # Skip confirmation prompt
```

### Managing Your Mounts

Each search creates its own organized collection folder:

```zsh
~/ArchiveMount/
├── classic_film_noir_1940s/
│   ├── TheStranger_0/
│   ├── ScarletStreet/
│   └── Hitch_Hiker/
├── hitchcock_psychological_thrillers/
│   ├── spellbound1945_202001/
│   └── gaslight-1944/
└── silent_comedies_charlie_chaplin/
    ├── Never_Weaken_1921/
    └── TheAdventurer1917/
```

**Manage mounts:**
```zsh
# List all active mounts
python3 mount_archive.py list

# Unmount a specific movie
python3 mount_archive.py unmount TheStranger_0

# Unmount everything
python3 mount_archive.py unmount-all
```

## Getting Started

This project is set up with Git flow branching:
- `main` - Production-ready code
- `develop` - Integration branch for features
- Feature branches - Individual features branched off develop

## Development Workflow

1. Create feature branches from `develop`
2. Merge completed features back to `develop`
3. When ready for release, merge `develop` to `main`