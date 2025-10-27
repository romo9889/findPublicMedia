# Streaming Feature — Technical Overview

## Architecture

The streaming feature consists of three main components:

### 1. `stream_now.py` — Core Streaming Engine
- **Metadata Resolution**: Fetches Archive.org item metadata via REST API
- **File Selection**: Intelligently picks best video (.mp4, .ogv) and subtitle (.srt, .vtt) files
- **Output Modes**:
  - **Quick Play**: Launches VLC with direct HTTP URLs (no download)
  - **Plex Mode (local)**: Mounts via rclone HTTP backend on your machine for Plex/Jellyfin
  - **Server Mode (remote)**: Sends a mount request to your configured server to mount the item remotely and create a Plex-compliant folder structure there

### 2. `vibe_streamer.py` — Integrated Workflow
- Extended with `--stream` and `--plex` flags
- Automatically resolves Archive.org items from search results
- Seamless search → stream pipeline

### 3. `mount_archive.py` — Mount Management
- List active mounts
- Unmount specific items or all items
- Helper for managing Plex libraries

## How It Works

### Quick Play Mode (VLC)

```
User Input → Archive.org Metadata API → Video URL + Subtitle URL → VLC
                                                                      ↓
                                              Subtitle converted (.vtt → .srt)
                                                                      ↓
                                                     VLC plays HTTP stream
```

**Advantages:**
- Instant playback (no waiting for downloads)
- Minimal disk usage (streams from Archive.org)
- Automatic subtitle handling

### Plex Mode (rclone)

```
User Input → Archive.org Metadata API → rclone HTTP backend config
                                                ↓
                                         Mount at ~/ArchiveMount/<id>
                                                ↓
                                         User adds to Plex library
                                                ↓
                                         Plex streams from Archive.org
```

**Advantages:**
- Persistent access (survives reboots with auto-mount)
- Native Plex interface
- Multiple items in one library
- Metadata scraping via Plex

## Technical Details

### Archive.org Metadata API

The metadata API returns JSON with file listings:

```json
{
  "files": [
    {
      "name": "movie.mp4",
      "size": "734003200",
      "format": "MPEG4"
    },
    {
      "name": "movie.srt",
      "size": "98304",
      "format": "SubRip"
    }
  ]
}
```

Our code:
1. Filters for video files (.mp4, .ogv, .mkv, .avi)
2. Prefers larger files (main feature vs trailer)
3. Matches subtitles (.srt preferred over .vtt)
4. Constructs direct download URLs

### rclone HTTP Backend

Mounts Archive.org items as read-only filesystems:

```ini
[archive_<identifier>]
type = http
url = https://archive.org/download/<identifier>/
```

Benefits:
- No authentication needed (public domain content)
- Works with any HTTP-accessible Archive.org item
- Compatible with Plex, Jellyfin, Emby, Kodi

### Subtitle Handling

Converts `.vtt` to `.srt` automatically:

1. **Preferred**: Uses `pysubs2` library (accurate)
2. **Fallback**: Naive regex replacement (good enough)

Subtitles are downloaded to temp files for VLC or kept on rclone mount for Plex.

## Cross-Platform Support

### macOS
- VLC path: `/Applications/VLC.app/Contents/MacOS/VLC`
- rclone via Homebrew: `brew install rclone`
- FUSE unmount: `fusermount -u` or `umount`

### Linux
- VLC via package manager: `sudo apt install vlc`
- rclone via curl: `curl https://rclone.org/install.sh | sudo bash`
- FUSE unmount: `fusermount -u`

## Error Handling

- **No video found**: Alerts user, suggests manual search
- **VLC not found**: Provides installation instructions
- **rclone not installed**: Provides installation commands
- **Metadata fetch fails**: Graceful fallback with error message
- **Subtitle conversion fails**: Continues without subtitles

## Performance

- **Metadata fetch**: ~1-2 seconds
- **VLC launch**: Instant (streams start immediately)
- **rclone mount**: ~2-3 seconds
- **Bandwidth**: Depends on video bitrate (typically 1-5 Mbps)

## Future Enhancements

- [ ] mpv player support (alternative to VLC)
- [ ] Jellyfin-specific mount helper
- [ ] Batch mount multiple items
- [ ] Resume playback position
- [ ] Download for offline viewing
- [ ] Quality selection (if multiple versions available)
