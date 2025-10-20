# 🤖 AI Mount List - Complete Guide

## Overview

The AI Mount List feature allows you to use natural language to describe movies you want to watch, and automatically mount multiple matching films from Archive.org for streaming through Plex or Jellyfin.

## Quick Start

### Basic Usage

```bash
# Interactive mode - prompts you for description
python3 ai_mount_list.py

# Command-line mode with prompt
python3 ai_mount_list.py --prompt "classic film noir from the 1940s"
```

### Common Use Cases

```bash
# Mount sci-fi movies (limit to 10)
python3 ai_mount_list.py --prompt "sci-fi movies about AI" --limit 10

# Mount without confirmation prompt
python3 ai_mount_list.py --prompt "hitchcock thrillers" --yes

# Custom mount location
python3 ai_mount_list.py --prompt "silent comedies" --mount-base /Volumes/External/Movies
```

## How It Works

### 1. You Describe What You Want

Use natural, conversational language:
- Genre-based: "film noir from the 1940s"
- Director-based: "hitchcock psychological thrillers"
- Theme-based: "sci-fi movies about artificial intelligence"
- Era-based: "comedies from the silent era"
- Star-based: "westerns with John Wayne"

### 2. AI Searches Multiple Sources

The script searches:
- **TMDB (The Movie Database)**: For comprehensive movie metadata
- **Archive.org**: For public domain and freely available films

It finds movies matching your description across both databases.

### 3. Intelligent Matching

The script:
- Ranks results by relevance
- Removes duplicates
- Verifies availability on Archive.org
- Filters out trailers and incomplete items

### 4. Batch Mount

For each movie found:
- Creates an rclone HTTP mount
- Configures mount point at `~/ArchiveMount/<identifier>`
- Verifies mount succeeded
- Reports progress

### 5. Ready for Plex

All mounted movies appear in `~/ArchiveMount/`:
```
~/ArchiveMount/
├── TheStranger_0/
│   ├── TheStranger_0.mp4
│   ├── TheStranger_0.srt
│   └── ...
├── ScarletStreet/
│   ├── ScarletStreet.mp4
│   └── ...
└── HitchHiker/
    └── ...
```

Point your Plex library at `~/ArchiveMount/` and scan!

## Command-Line Options

```
usage: ai_mount_list.py [--prompt TEXT] [--limit N] [--mount-base PATH] [--yes]

Options:
  --prompt TEXT       Natural language movie description
                      If not provided, enters interactive mode
  
  --limit N           Maximum number of movies to find and mount
                      Default: 20
                      Range: 1-100
  
  --mount-base PATH   Base directory for mounts
                      Default: ~/ArchiveMount
  
  --yes, -y           Skip confirmation prompt
                      Mounts immediately without asking
```

## Example Prompts

### By Genre

```bash
# Film Noir
python3 ai_mount_list.py --prompt "film noir from the 1940s"

# Science Fiction
python3 ai_mount_list.py --prompt "classic sci-fi movies"

# Horror
python3 ai_mount_list.py --prompt "horror films from the 1930s"

# Western
python3 ai_mount_list.py --prompt "western movies"

# Comedy
python3 ai_mount_list.py --prompt "silent comedies with charlie chaplin"
```

### By Director

```bash
# Alfred Hitchcock
python3 ai_mount_list.py --prompt "hitchcock suspense thrillers"

# Fritz Lang
python3 ai_mount_list.py --prompt "fritz lang expressionist films"

# Orson Welles
python3 ai_mount_list.py --prompt "orson welles movies"
```

### By Theme

```bash
# AI/Technology
python3 ai_mount_list.py --prompt "movies about artificial intelligence"

# Time Travel
python3 ai_mount_list.py --prompt "time travel science fiction"

# Space
python3 ai_mount_list.py --prompt "space exploration movies"
```

### By Era

```bash
# Silent Era
python3 ai_mount_list.py --prompt "silent films from the 1920s"

# Golden Age
python3 ai_mount_list.py --prompt "golden age hollywood movies from the 1940s"

# Atomic Age
python3 ai_mount_list.py --prompt "1950s sci-fi about nuclear monsters"
```

## Managing Your Collection

### List Active Mounts

```bash
python3 mount_archive.py list
```

Output:
```
Active Archive.org mounts:
  - TheStranger_0 → /Users/you/ArchiveMount/TheStranger_0
  - ScarletStreet → /Users/you/ArchiveMount/ScarletStreet
  - HitchHiker → /Users/you/ArchiveMount/HitchHiker
```

### Unmount Specific Movie

```bash
python3 mount_archive.py unmount TheStranger_0
```

### Unmount All

```bash
python3 mount_archive.py unmount-all
```

## Results File

Each run saves a detailed JSON report to `mount_results.json`:

```json
{
  "total": 5,
  "mounted": 4,
  "failed": 1,
  "skipped": 0,
  "details": [
    {
      "title": "The Stranger",
      "identifier": "TheStranger_0",
      "status": "mounted",
      "path": "/Users/you/ArchiveMount/TheStranger_0"
    },
    ...
  ]
}
```

## Troubleshooting

### No Movies Found

**Issue:** "No movies found matching your description."

**Solutions:**
1. Try a broader description: "film noir" instead of "film noir with femme fatales from 1947"
2. Check your TMDB API key is set: `echo $TMDB_API_KEY`
3. Try searching Archive.org directly: https://archive.org/details/movies

### Mount Failures

**Issue:** Movies found but mounts fail.

**Solutions:**
1. Check rclone is installed: `rclone version`
2. Ensure macFUSE is allowed in System Settings → Privacy & Security
3. Check available disk space: `df -h ~`
4. Try mounting one movie manually to see error:
   ```bash
   python3 stream_now.py --ia-link "https://archive.org/details/TheStranger_0" --mode plex
   ```

### Plex Not Showing Movies

**Issue:** Mounts successful but Plex shows no content.

**Solutions:**
1. Verify mounts are active: `python3 mount_archive.py list`
2. Check files are visible: `ls -la ~/ArchiveMount/TheStranger_0/`
3. In Plex, go to Library → Scan Library Files
4. Check Plex has permission to read ~/ArchiveMount:
   - System Settings → Privacy & Security → Files and Folders
   - Allow Plex Media Server to access your home folder

### Rate Limiting

**Issue:** TMDB API rate limit errors.

**Solution:** The script automatically falls back to Archive.org search. Wait a minute and try again, or use smaller `--limit` values.

## Advanced Usage

### Building Themed Collections

```bash
# 1940s Film Noir Collection
python3 ai_mount_list.py --prompt "film noir from the 1940s" --limit 15 --yes

# Sci-Fi Collection
python3 ai_mount_list.py --prompt "science fiction movies" --limit 20 --yes

# Horror Collection  
python3 ai_mount_list.py --prompt "classic horror films" --limit 10 --yes
```

### Scripted Batch Operations

Create a script to build multiple collections:

```bash
#!/bin/bash
# build_collections.sh

echo "Building Film Noir collection..."
python3 ai_mount_list.py --prompt "film noir 1940s" --limit 10 --yes

echo "Building Sci-Fi collection..."
python3 ai_mount_list.py --prompt "classic sci-fi" --limit 10 --yes

echo "Building Horror collection..."
python3 ai_mount_list.py --prompt "horror movies 1930s" --limit 10 --yes

echo "All collections mounted!"
python3 mount_archive.py list
```

### Custom Mount Locations

Mount different genres to different locations:

```bash
# Noir collection
python3 ai_mount_list.py --prompt "film noir" --mount-base ~/Movies/Noir --yes

# Sci-Fi collection
python3 ai_mount_list.py --prompt "sci-fi" --mount-base ~/Movies/SciFi --yes
```

Then create separate Plex libraries for each genre:
- Noir → `~/Movies/Noir`
- Sci-Fi → `~/Movies/SciFi`

## Integration with Plex

### One-Time Setup

1. Mount your first collection:
   ```bash
   python3 ai_mount_list.py --prompt "classic movies" --limit 10
   ```

2. Add to Plex:
   - Open Plex Web UI
   - Add Library → Movies
   - Add Folder → `~/ArchiveMount`
   - Scan

### Adding More Movies

Just run the script again with new prompts:
```bash
python3 ai_mount_list.py --prompt "hitchcock movies" --yes
```

Plex will automatically detect new mounts on its next scan, or manually trigger:
- Library → ... → Scan Library Files

## Performance Tips

### Faster Searches

- Use specific prompts for better results
- Set reasonable `--limit` values (5-20 is usually enough)
- Use `--yes` flag to skip confirmation

### Mount Management

- Unmount movies you're done watching to save resources:
  ```bash
  python3 mount_archive.py unmount TheStranger_0
  ```
- Keep your mount directory organized
- Periodically run `mount_archive.py list` to see what's active

### Network Efficiency

- rclone caches files automatically (`--vfs-cache-mode full`)
- First playback may buffer, subsequent plays are faster
- Consider your internet speed when mounting many large films

## Examples

### Example 1: Weekend Movie Marathon

```bash
# Friday: Mount a film noir collection
python3 ai_mount_list.py --prompt "film noir detective movies 1940s" --limit 5 --yes

# Saturday: Add some sci-fi
python3 ai_mount_list.py --prompt "1950s science fiction" --limit 5 --yes

# Sunday: Clean up what you watched
python3 mount_archive.py unmount-all
```

### Example 2: Director Retrospective

```bash
# Mount all available Hitchcock films
python3 ai_mount_list.py --prompt "alfred hitchcock movies" --limit 20 --yes

# Point Plex to the mounts
# Watch through them over the month

# Keep them mounted as long as you want!
```

### Example 3: Genre Study

```bash
# Build a comprehensive noir collection
python3 ai_mount_list.py --prompt "film noir movies 1940s 1950s" --limit 30 --yes

# Create a Plex collection in the UI
# Tag all the noir films
# Share with friends via Plex
```

## FAQ

**Q: How many movies can I mount at once?**
A: Technically unlimited, but we recommend 20-50 active mounts for performance. You can always unmount and remount as needed.

**Q: Do the mounts persist after reboot?**
A: No, rclone mounts are not permanent. Rerun the script after reboot, or create a startup script.

**Q: Can I download the movies?**
A: This tool streams content. To download, visit Archive.org directly. Note that public domain content is freely downloadable.

**Q: Does this work with Jellyfin?**
A: Yes! Jellyfin works the same way as Plex - just point it to `~/ArchiveMount`.

**Q: Can I use this on Linux or Windows?**
A: Yes, but you may need to adjust the mount base path and ensure rclone/FUSE are properly installed.

**Q: What if a movie isn't on Archive.org?**
A: The script only mounts movies available on Archive.org (public domain/freely licensed content). Not all movies will be available.

## Tips for Better Results

1. **Be Specific But Not Too Specific**
   - Good: "film noir from the 1940s"
   - Too vague: "movies"
   - Too specific: "film noir with venetian blinds shot by John Alton in 1947"

2. **Use Recognized Film Terminology**
   - Genre names: noir, western, sci-fi, horror
   - Eras: silent era, golden age, new wave
   - Directors: hitchcock, welles, lang

3. **Combine Multiple Attributes**
   - "1950s sci-fi about space"
   - "silent comedies with slapstick"
   - "hitchcock suspense thrillers"

4. **Experiment!**
   - Try different phrasings
   - Use the interactive mode to iterate
   - Check what's mounted with `mount_archive.py list`

## Contributing

Found a good search technique? Have ideas for better AI matching? Contributions welcome!

---

**Enjoy your AI-powered movie collection! 🎬🤖**
