# Public Media Mounter

Mount movies from Archive.org to your Plex server or local machine with proper Plex folder structure.

## 🚀 Quick Start

```bash
python3 main.py
```

The app will ask you:
1. **What to mount**: Collection (batch) or Single movie
2. **Where to mount**: Server (remote Plex) or Local

## 📋 Prerequisites

### For All Users
- Python 3.8+
- Archive.org public domain content only

### For Local Mounting
- **rclone**: `brew install rclone` (macOS) or `curl https://rclone.org/install.sh | sudo bash` (Linux)
- Mounts to: `~/ArchiveMount/<collection_name>/`

### For Server Mounting (Recommended)
- A remote server with SSH access
- rclone installed on the server
- Plex Media Server installed on the server
- SSH key authentication set up

## 🎬 Features

### 1. Mount a Collection (AI-Powered)
Search using natural language and mount multiple movies at once:

```
Your description: classic film noir from the 1940s
How many movies: 15
```

The app will:
- Search TMDB and Archive.org
- Find up to 15 matching movies
- Mount them with proper Plex structure: `Movie Name (Year)/Movie Name (Year).ext`

Examples:
- "sci-fi movies about AI"
- "hitchcock thrillers"
- "silent comedies charlie chaplin"

### 2. Mount a Single Movie
Mount one specific movie:

```
Archive.org link/ID: https://archive.org/details/HisGirlFriday1940
```

Or just the identifier:
```
Archive.org link/ID: HisGirlFriday1940
```

## 🖥️ Server Setup

First time using server mode? The app will guide you through setup:

1. SSH host (e.g., `138.199.161.86`)
2. SSH user (e.g., `root`)
3. SSH port (default: `22`)
4. Remote mount path (e.g., `/home/root/PlexMovies`)

Server requirements:
- Ubuntu/Debian Linux
- rclone installed: `curl https://rclone.org/install.sh | sudo bash`
- Plex Media Server installed
- SSH key authentication configured

### Server Configuration

Config is saved to `~/.plex_server_config.json` (not committed to git):

```json
{
  "host": "138.199.161.86",
  "user": "root",
  "port": 22,
  "remote_path": "/home/root/PlexMovies"
}
```

## 📁 Plex Structure

All mounts follow Plex best practices:

```
PlexMovies/
├── His Girl Friday (1940)/
│   └── His Girl Friday (1940).mp4  → symlink to raw mount
├── Night of the Living Dead (1968)/
│   └── Night of the Living Dead (1968).mp4  → symlink
└── ArchiveMount_raw/
    ├── HisGirlFriday1940/
    │   └── [actual rclone mount files]
    └── night_of_the_living_dead/
        └── [actual rclone mount files]
```

### Why This Structure?

- **Plex-compliant naming**: Movie Name (Year)/Movie Name (Year).ext
- **Efficient storage**: Symlinks point to actual mounts (no duplication)
- **Clean library**: Only properly named folders appear in Plex
- **Raw access**: Original mounts preserved in `ArchiveMount_raw/`

## 🔧 Advanced Usage

### Environment Variables

**Optional TMDB API Key** (improves search results):
```bash
export TMDB_API_KEY="your_tmdb_v3_api_key"
```

Get a free key at https://www.themoviedb.org/settings/api

### Direct Script Usage

If you prefer command-line:

```bash
# Mount a collection on server
python3 ai_mount_list.py --server --prompt "film noir 1940s" --limit 20

# Mount single movie on server
python3 stream_now.py --ia-link "https://archive.org/details/..." --mode server

# Mount single movie locally
python3 stream_now.py --ia-link "https://archive.org/details/..." --mode plex
```

## 📚 How It Works

### Server Mounting
1. SSH to your server
2. Create rclone HTTP remote for Archive.org item
3. Mount item to `ArchiveMount_raw/<identifier>/`
4. Find best video file (mp4 > mkv > avi)
5. Create Plex folder: `Movie Name (Year)/`
6. Create symlink to best video with Plex-compliant name
7. Tell Plex to scan library

### Local Mounting
1. Create rclone HTTP remote for Archive.org item
2. Mount to `~/ArchiveMount/<collection>/<identifier>/`
3. Add mount location to your Plex library
4. Plex scans and imports

## 🛠️ Troubleshooting

### "rclone not found"
```bash
# macOS
brew install rclone

# Linux
curl https://rclone.org/install.sh | sudo bash
```

### "SSH connection failed"
- Ensure SSH key authentication is set up
- Test: `ssh user@your-server "echo OK"`
- Add key to agent: `ssh-add ~/.ssh/id_rsa`

### "No video files found"
Some Archive.org items don't contain video files. The script will skip these automatically.

### Plex not seeing new movies
1. Go to Plex settings → Libraries
2. Find your Movies library
3. Click the "..." menu → Scan Library Files

## 📖 Documentation

- `SERVER_SETUP.md` - Detailed server configuration guide
- `AI_MOUNT_GUIDE.md` - AI search tips and examples

## 🗂️ Project Structure

### Core Scripts
- `main.py` - Main entry point (unified interface)
- `ai_mount_list.py` - AI-powered collection mounting
- `stream_now.py` - Single movie mounting
- `server_mount_plex.py` - Server-side mounting with Plex structure
- `setup_server.py` - Server configuration wizard

### Supporting Scripts
- `vibe_streamer.py` - TMDB/Archive.org search utilities
- `create_plex_library.py` - Local Plex library organizer

## 🤝 Contributing

This project mounts public domain content from Archive.org only. All content is legally available for streaming and downloading.

## 📄 License

MIT License - See LICENSE file for details

---

**Note**: This tool only works with public domain movies available on Archive.org. It does not bypass any copyright protections or enable piracy.
