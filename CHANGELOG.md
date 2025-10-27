# Changelog

## v2.0.0 - Streamlined Release (2025-10-27)

### 🎯 Major Refactoring
Complete restructure of the project to focus on core mounting functionality with a unified entry point.

### ✨ New Features
- **Unified Entry Point (`main.py`)**: Single interactive interface for all mounting operations
  - Mount collections via AI search
  - Mount single movies
  - Automatic server/local routing
  - Integrated server setup
- **Quick Start Script (`start.sh`)**: Simple bash launcher for main.py

### 🗑️ Removed Files
Cleaned up unnecessary scripts and documentation:
- `copy_to_server_direct.py` - superseded by server_mount_plex.py
- `demo.sh` - no longer needed with unified interface
- `demo_ai_mount.sh` - functionality integrated into main.py
- `mount_archive.py` - mount management now via main interface
- `reorganize_mounts.py` - one-time utility, no longer needed
- `test_ssh_connection.py` - connection testing built into setup
- `translate_and_sync.py` - unrelated utility
- `update_mount_scripts.py` - no longer needed
- `server_mount.py` - merged into server_mount_plex.py
- `PLEX_GUIDE.md` - consolidated into README
- `QUICKSTART_AI_MOUNT.md` - consolidated into README
- `STREAMING.md` - consolidated into README
- `scripts/` - empty directory removed

### 📝 Updated Documentation
- **README.md**: Complete rewrite with focus on quick start and core features
- **AI_MOUNT_GUIDE.md**: Updated to reference main.py and server mode
- **.gitignore**: Added mount_list.json, removed outdated exclusions

### 🔧 Enhanced Scripts
- **ai_mount_list.py**: Added `--server` flag for direct server mounting
- **stream_now.py**: Added `server` mode to mount directly on remote server
- **server_mount_plex.py**: Added CLI arguments for non-interactive batch/single mounts
- **setup_server.py**: Improved to work with interactive SSH passphrases

### 🎬 Project Focus
The app now has a single, clear purpose:
- Mount Archive.org movies to Plex server or local machine
- Support both AI-powered collections and single movies
- Follow Plex naming best practices
- Work seamlessly with remote servers

### 📁 Current File Structure
```
findPublicMedia/
├── main.py                    # ⭐ Main entry point
├── start.sh                   # Quick launcher
├── ai_mount_list.py          # AI collection mounting
├── stream_now.py             # Single movie mounting
├── server_mount_plex.py      # Server-side Plex structure creation
├── setup_server.py           # Server configuration wizard
├── create_plex_library.py    # Local Plex library organizer
├── vibe_streamer.py          # TMDB/Archive.org search utilities
├── README.md                 # Quick start guide
├── AI_MOUNT_GUIDE.md         # AI search examples
├── SERVER_SETUP.md           # Server configuration guide
└── SERVER_SECURITY.md        # Security best practices
```

### 🚀 Usage
```bash
# Simple start
python3 main.py

# Or
./start.sh

# Direct commands still available
python3 ai_mount_list.py --server --prompt "film noir 1940s"
python3 stream_now.py --ia-link "..." --mode server
```

### 🔐 Security
- Server credentials stored in `~/.plex_server_config.json` (gitignored)
- No credentials committed to repository
- Interactive SSH prompts supported

---

## v1.0.0 - Initial Release
- Basic streaming feature
- AI-powered mount lists
- Server copying functionality
- Local Plex library organization
