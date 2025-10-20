#!/usr/bin/env python3
"""
Stream Now: Instantly play Archive.org movies via VLC or mount for Plex.

Usage:
  python stream_now.py --ia-link "https://archive.org/details/HisGirlFriday1940" --mode quick
  python stream_now.py --ia-link "https://archive.org/details/HisGirlFriday1940" --mode plex

Modes:
  quick - Open movie + subtitles directly in VLC (instant playback)
  plex  - Mount Archive.org item via rclone for Plex/Jellyfin (persistent streaming)

Requirements:
  - VLC (for quick mode)
  - rclone (for plex mode)
  - pysubs2 (optional, for .vtt to .srt conversion)
"""
import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Constants
ARCHIVE_METADATA_URL = "https://archive.org/metadata/"
ARCHIVE_DOWNLOAD_URL = "https://archive.org/download/"


def log(phase: str, message: str):
    """Log progress with clear phase markers."""
    print(f"[{phase.upper()}] {message}")


def detect_os() -> str:
    """Detect current operating system."""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"


def extract_identifier(ia_link: str) -> Optional[str]:
    """Extract Archive.org identifier from URL.
    
    Supports:
    - https://archive.org/details/IDENTIFIER
    - https://archive.org/download/IDENTIFIER/file.mp4
    """
    ia_link = ia_link.strip()
    
    # Direct file link
    if "/download/" in ia_link:
        parts = ia_link.split("/download/")[1].split("/")
        return parts[0] if parts else None
    
    # Item details page
    if "/details/" in ia_link:
        parts = ia_link.split("/details/")[1].split("/")
        return parts[0] if parts else None
    
    return None


def fetch_metadata(identifier: str) -> Optional[Dict[str, Any]]:
    """Fetch Archive.org metadata for given identifier."""
    log("resolve", f"Fetching metadata for: {identifier}")
    try:
        url = f"{ARCHIVE_METADATA_URL}{urllib.parse.quote(identifier)}"
        with urllib.request.urlopen(url, timeout=20) as resp:
            data = json.load(resp)
        return data
    except Exception as e:
        log("error", f"Failed to fetch metadata: {e}")
        return None


def find_video_and_subtitle(metadata: Dict[str, Any], identifier: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract best video file and subtitle file URLs from metadata.
    
    Returns:
        (video_url, subtitle_url) tuple
    """
    files = metadata.get("files", [])
    
    video_url = None
    subtitle_url = None
    
    # Preference order for video: mp4 > ogv > mkv > avi
    video_exts = [".mp4", ".ogv", ".mkv", ".avi"]
    subtitle_exts = [".srt", ".vtt"]
    
    video_candidates = []
    subtitle_candidates = []
    
    for f in files:
        name = f.get("name", "").lower()
        
        # Skip very small files (likely samples/previews)
        size = f.get("size", 0)
        if isinstance(size, str):
            try:
                size = int(size)
            except:
                size = 0
        
        # Collect video candidates
        for ext in video_exts:
            if name.endswith(ext):
                # Prefer larger files (main feature vs trailer)
                video_candidates.append((size, name, ext))
                break
        
        # Collect subtitle candidates
        for ext in subtitle_exts:
            if name.endswith(ext):
                subtitle_candidates.append((name, ext))
                break
    
    # Pick best video (largest file with preferred extension)
    if video_candidates:
        video_candidates.sort(reverse=True)  # Sort by size descending
        _, video_name, _ = video_candidates[0]
        video_url = f"{ARCHIVE_DOWNLOAD_URL}{urllib.parse.quote(identifier)}/{urllib.parse.quote(video_name)}"
        log("resolve", f"Found video: {video_name}")
    
    # Pick best subtitle (.srt preferred over .vtt)
    if subtitle_candidates:
        # Sort: .srt first
        subtitle_candidates.sort(key=lambda x: (0 if x[1] == ".srt" else 1, x[0]))
        subtitle_name, _ = subtitle_candidates[0]
        subtitle_url = f"{ARCHIVE_DOWNLOAD_URL}{urllib.parse.quote(identifier)}/{urllib.parse.quote(subtitle_name)}"
        log("resolve", f"Found subtitle: {subtitle_name}")
    
    return video_url, subtitle_url


def download_subtitle(subtitle_url: str, dest_path: str) -> bool:
    """Download subtitle file to local path."""
    log("prepare", f"Downloading subtitle: {subtitle_url}")
    try:
        with urllib.request.urlopen(subtitle_url, timeout=30) as resp:
            with open(dest_path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        log("error", f"Failed to download subtitle: {e}")
        return False


def convert_vtt_to_srt(vtt_path: str, srt_path: str) -> bool:
    """Convert VTT subtitle to SRT format."""
    log("prepare", "Converting .vtt to .srt")
    try:
        import pysubs2
        subs = pysubs2.load(vtt_path)
        subs.save(srt_path, format_="srt")
        return True
    except ImportError:
        log("warn", "pysubs2 not installed, using naive conversion")
        # Naive fallback
        try:
            with open(vtt_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            text = text.replace("WEBVTT", "").strip()
            text = text.replace(".", ",")  # Timestamp format
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(text)
            return True
        except Exception as e:
            log("error", f"VTT conversion failed: {e}")
            return False
    except Exception as e:
        log("error", f"VTT conversion failed: {e}")
        return False


def quick_play_vlc(video_url: str, subtitle_url: Optional[str], os_type: str):
    """Launch VLC with video and optional subtitle."""
    log("play", "Launching VLC player...")
    
    # Determine VLC command based on OS
    if os_type == "macos":
        vlc_cmd = "/Applications/VLC.app/Contents/MacOS/VLC"
        if not os.path.exists(vlc_cmd):
            vlc_cmd = "vlc"  # Try PATH
    else:
        vlc_cmd = "vlc"
    
    cmd = [vlc_cmd, video_url]
    
    # Handle subtitle
    subtitle_file = None
    if subtitle_url:
        # Download subtitle to temp file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.srt', delete=False) as tmp:
            subtitle_file = tmp.name
        
        if subtitle_url.lower().endswith('.vtt'):
            vtt_tmp = subtitle_file.replace('.srt', '.vtt')
            if download_subtitle(subtitle_url, vtt_tmp):
                if not convert_vtt_to_srt(vtt_tmp, subtitle_file):
                    subtitle_file = None
                try:
                    os.remove(vtt_tmp)
                except:
                    pass
        else:
            if not download_subtitle(subtitle_url, subtitle_file):
                subtitle_file = None
        
        if subtitle_file:
            cmd.extend(["--sub-file", subtitle_file])
    
    try:
        log("play", f"Running: {' '.join(cmd[:2])}...")
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("\n✅ SUCCESS! VLC is now playing your movie.")
        if subtitle_file:
            print(f"   Subtitles loaded from: {subtitle_file}")
        print(f"   Video: {video_url}")
    except FileNotFoundError:
        log("error", "VLC not found. Please install VLC media player:")
        if os_type == "macos":
            print("   brew install --cask vlc")
        else:
            print("   sudo apt install vlc  (or your distro's package manager)")
        sys.exit(1)
    except Exception as e:
        log("error", f"Failed to launch VLC: {e}")
        sys.exit(1)


def mount_for_plex(identifier: str, video_url: str, subtitle_url: Optional[str], os_type: str):
    """Mount Archive.org item via rclone for Plex/Jellyfin."""
    log("mount", "Setting up rclone HTTP mount for Plex...")
    
    # Check if rclone is installed
    try:
        subprocess.run(["rclone", "version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        log("error", "rclone not found. Please install it:")
        if os_type == "macos":
            print("   brew install rclone")
        else:
            print("   curl https://rclone.org/install.sh | sudo bash")
        sys.exit(1)
    
    # Create mount point in "searched_for" collection
    mount_dir = Path.home() / "ArchiveMount" / "searched_for" / identifier
    mount_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract base URL for the item
    base_url = f"{ARCHIVE_DOWNLOAD_URL}{urllib.parse.quote(identifier)}/"
    
    # Create rclone config for this mount
    config_name = f"archive_{identifier}"
    
    log("mount", f"Configuring rclone remote: {config_name}")
    
    # Write rclone config
    config_content = f"""[{config_name}]
type = http
url = {base_url}
"""
    
    rclone_config_dir = Path.home() / ".config" / "rclone"
    rclone_config_dir.mkdir(parents=True, exist_ok=True)
    rclone_config_file = rclone_config_dir / "rclone.conf"
    
    # Append or update config
    existing_config = ""
    if rclone_config_file.exists():
        existing_config = rclone_config_file.read_text()
    
    if config_name not in existing_config:
        with open(rclone_config_file, "a") as f:
            f.write("\n" + config_content)
    
    # Mount command
    mount_cmd = [
        "rclone", "mount",
        f"{config_name}:", str(mount_dir),
        "--read-only",
        "--vfs-cache-mode", "full",
        "--daemon"
    ]
    
    log("mount", f"Mounting to: {mount_dir}")
    try:
        subprocess.run(mount_cmd, check=True)
        
        print("\n✅ SUCCESS! Archive.org item mounted for Plex.")
        print(f"\n📁 Mount Location: {mount_dir}")
        print(f"\n📺 Next Steps:")
        print(f"   1. Open Plex or Jellyfin")
        print(f"   2. Add a new Movie library")
        print(f"   3. Point it to: {mount_dir}")
        print(f"   4. Scan library and enjoy!\n")
        print(f"🔧 To unmount later, run:")
        print(f"   umount {mount_dir}  (Linux)")
        print(f"   or")
        print(f"   fusermount -u {mount_dir}  (macOS/Linux with FUSE)")
        
    except subprocess.CalledProcessError as e:
        log("error", f"rclone mount failed: {e}")
        print("\nTry running the mount command manually:")
        print(f"  {' '.join(mount_cmd)}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Stream Archive.org movies instantly via VLC or mount for Plex."
    )
    parser.add_argument(
        "--ia-link",
        required=True,
        help="Archive.org link (e.g., https://archive.org/details/HisGirlFriday1940)"
    )
    parser.add_argument(
        "--mode",
        choices=["quick", "plex"],
        default="quick",
        help="Playback mode: 'quick' (VLC) or 'plex' (rclone mount)"
    )
    
    args = parser.parse_args()
    
    # Detect OS
    os_type = detect_os()
    log("system", f"Detected OS: {os_type}")
    
    # Extract identifier
    identifier = extract_identifier(args.ia_link)
    if not identifier:
        log("error", f"Could not extract identifier from: {args.ia_link}")
        sys.exit(1)
    
    log("resolve", f"Archive.org identifier: {identifier}")
    
    # Fetch metadata
    metadata = fetch_metadata(identifier)
    if not metadata:
        log("error", "Failed to retrieve metadata. Check your link and try again.")
        sys.exit(1)
    
    # Find video and subtitle
    video_url, subtitle_url = find_video_and_subtitle(metadata, identifier)
    
    if not video_url:
        log("error", "No playable video file found in this Archive.org item.")
        sys.exit(1)
    
    # Execute based on mode
    if args.mode == "quick":
        quick_play_vlc(video_url, subtitle_url, os_type)
    elif args.mode == "plex":
        mount_for_plex(identifier, video_url, subtitle_url, os_type)


if __name__ == "__main__":
    main()
