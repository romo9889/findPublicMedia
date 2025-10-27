#!/usr/bin/env python3
"""
Mount Archive.org items on server with Plex-compliant structure.

Structure created:
  /home/root/PlexMovies/
    Movie Name (Year)/
      Movie Name (Year).mp4  (symlink to best video in mount)

This follows Plex best practices for movie libraries.
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path

CONFIG_PATH = os.path.expanduser("~/.plex_server_config.json")


def load_config():
    """Load server configuration."""
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ Config not found: {CONFIG_PATH}")
        print("   Please run: python3 setup_server.py first")
        sys.exit(1)
    
    with open(CONFIG_PATH) as f:
        return json.load(f)


def extract_year(identifier, title):
    """Extract year from identifier or title."""
    # Try identifier first (often has year)
    year_match = re.search(r'(19\d{2}|20\d{2})', identifier)
    if year_match:
        return year_match.group(1)
    
    # Try title
    year_match = re.search(r'(19\d{2}|20\d{2})', title)
    if year_match:
        return year_match.group(1)
    
    return None


def clean_title(title, identifier):
    """Clean title for Plex folder name."""
    # Remove Archive.org suffixes
    cleaned = re.sub(r'_\d{6}$', '', title)
    cleaned = re.sub(r'\s*\(.*?\)\s*$', '', cleaned)
    
    # If title is just the identifier, try to make it readable
    if cleaned.lower().replace('_', '').replace('-', '') == identifier.lower().replace('_', '').replace('-', ''):
        # Convert snake_case or kebab-case to Title Case
        cleaned = identifier.replace('_', ' ').replace('-', ' ')
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
    
    # Remove special characters that might cause issues
    cleaned = re.sub(r'[<>:"/\\|?*]', '', cleaned)
    
    return cleaned.strip()


def mount_archive_raw(config, identifier):
    """
    Mount Archive.org item to temporary location on server.
    Returns mount path or None if failed.
    """
    remote_mount_base = f"{config['remote_path']}/ArchiveMount_raw"
    remote_mount_point = f"{remote_mount_base}/{identifier}"
    
    # Create mount point
    mkdir_cmd = [
        'ssh', '-p', config['port'],
        f"{config['username']}@{config['host']}",
        f'mkdir -p "{remote_mount_point}"'
    ]
    subprocess.run(mkdir_cmd, capture_output=True)
    
    # Create rclone remote config
    remote_name = f"archive_{identifier.replace('-', '_')[:50]}"
    base_url = f"https://archive.org/download/{identifier}/"
    
    rclone_config_cmd = [
        'ssh', '-p', config['port'],
        f"{config['username']}@{config['host']}",
        f'rclone config create {remote_name} http url {base_url} 2>/dev/null || true'
    ]
    subprocess.run(rclone_config_cmd, capture_output=True)
    
    # Mount using rclone
    mount_cmd = [
        'ssh', '-p', config['port'],
        f"{config['username']}@{config['host']}",
        f'nohup rclone mount {remote_name}: "{remote_mount_point}" '
        f'--daemon --vfs-cache-mode writes --allow-other > /dev/null 2>&1 &'
    ]
    
    result = subprocess.run(mount_cmd, capture_output=True)
    if result.returncode == 0:
        return remote_mount_point
    return None


def find_best_video_on_server(config, mount_path):
    """Find the best video file in the mount on the server."""
    # List files and find best video
    list_cmd = [
        'ssh', '-p', config['port'],
        f"{config['username']}@{config['host']}",
        f'find "{mount_path}" -type f \\( -iname "*.mp4" -o -iname "*.mkv" -o -iname "*.avi" \\) '
        f'! -iname "*512kb*" ! -iname "*.thumbs" ! -iname "*_thumb.jpg" 2>/dev/null | head -20'
    ]
    
    result = subprocess.run(list_cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    
    videos = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    
    if not videos:
        return None
    
    # Prefer mp4 > mkv > avi
    for ext in ['.mp4', '.mkv', '.avi']:
        for video in videos:
            if video.lower().endswith(ext) and '512kb' not in video.lower():
                return video
    
    return videos[0] if videos else None


def create_plex_structure(config, identifier, title, year=None):
    """
    Create Plex-compliant structure on server:
    1. Mount Archive.org item to raw location
    2. Find best video file
    3. Create Plex folder: Movie Name (Year)/
    4. Create symlink: Movie Name (Year).ext → best video
    """
    print(f"\n📦 Processing: {title}")
    print(f"   ID: {identifier}")
    
    # Mount to raw location
    print("   ⏳ Mounting Archive.org item...")
    raw_mount = mount_archive_raw(config, identifier)
    if not raw_mount:
        print("   ❌ Failed to mount")
        return False
    
    # Wait for mount to stabilize
    import time
    time.sleep(3)
    
    # Find best video
    print("   ⏳ Finding best video file...")
    best_video = find_best_video_on_server(config, raw_mount)
    if not best_video:
        print("   ❌ No video files found")
        return False
    
    video_name = best_video.split('/')[-1]
    print(f"   ✓ Found: {video_name}")
    
    # Clean title and create Plex folder name
    clean_name = clean_title(title, identifier)
    if year:
        plex_folder = f"{clean_name} ({year})"
    else:
        plex_folder = clean_name
    
    # Create Plex directory structure
    plex_base = config['remote_path']
    plex_movie_dir = f"{plex_base}/{plex_folder}"
    
    print(f"   ⏳ Creating Plex structure: {plex_folder}/")
    mkdir_plex = [
        'ssh', '-p', config['port'],
        f"{config['username']}@{config['host']}",
        f'mkdir -p "{plex_movie_dir}"'
    ]
    subprocess.run(mkdir_plex, capture_output=True)
    
    # Determine video extension
    video_ext = best_video.split('.')[-1]
    symlink_name = f"{plex_folder}.{video_ext}"
    symlink_path = f"{plex_movie_dir}/{symlink_name}"
    
    # Create symlink
    print(f"   ⏳ Creating symlink...")
    symlink_cmd = [
        'ssh', '-p', config['port'],
        f"{config['username']}@{config['host']}",
        f'ln -sf "{best_video}" "{symlink_path}"'
    ]
    
    result = subprocess.run(symlink_cmd, capture_output=True)
    if result.returncode == 0:
        print(f"   ✅ Created: {plex_folder}/{symlink_name}")
        return True
    else:
        print(f"   ❌ Failed to create symlink")
        return False


def process_mount_list(config, mount_list_file="mount_list.json"):
    """Process all items from mount_list.json."""
    if not os.path.exists(mount_list_file):
        print(f"❌ Mount list not found: {mount_list_file}")
        return False
    
    with open(mount_list_file) as f:
        items = json.load(f)
    
    print(f"\n📋 Found {len(items)} items to process")
    print("="*70)
    
    success = 0
    failed = 0
    
    for i, item in enumerate(items, 1):
        identifier = item.get('identifier')
        title = item.get('title', identifier)
        
        if not identifier:
            print(f"\n[{i}/{len(items)}] ⏭️  Skipping (no identifier): {title}")
            failed += 1
            continue
        
        # Extract year
        year = extract_year(identifier, title)
        
        print(f"\n[{i}/{len(items)}] {title}" + (f" ({year})" if year else ""))
        print("-"*70)
        
        if create_plex_structure(config, identifier, title, year):
            success += 1
        else:
            failed += 1
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"✅ Success: {success}")
    print(f"❌ Failed:  {failed}")
    print(f"📁 Plex library: {config['remote_path']}/")
    print("\n💡 Add this path to your Plex movie library!")
    
    return True


def main():
    config = load_config()
    
    print("\n" + "="*70)
    print("  🎬 Server Mount with Plex Structure")
    print("="*70)
    print(f"\n🌐 Server: {config['host']}")
    print(f"👤 User: {config['username']}")
    print(f"📁 Plex library: {config['remote_path']}/")
    print("\n📐 Structure: Movie Name (Year)/Movie Name (Year).ext")
    
    # Check if mount_list.json exists
    if not os.path.exists("mount_list.json"):
        print("\n❌ mount_list.json not found")
        print("   Create it first with ai_mount_list.py or manually")
        sys.exit(1)
    
    proceed = input("\n🚀 Process mount_list.json? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    process_mount_list(config)


if __name__ == "__main__":
    # Add lightweight CLI so this can run non-interactively for single ids or a json list
    import argparse

    parser = argparse.ArgumentParser(
        description="Mount Archive.org items on the server with Plex-compliant structure"
    )
    parser.add_argument(
        "--json",
        dest="json_file",
        help="Path to mount_list.json (process all items in the file)"
    )
    parser.add_argument(
        "--identifier",
        help="Archive.org identifier to mount as a single item"
    )
    parser.add_argument(
        "--title",
        help="Optional display title for the single item (used for Plex folder name)"
    )
    parser.add_argument(
        "--year",
        help="Optional year for the single item"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without interactive prompts"
    )

    args, unknown = parser.parse_known_args()

    # If arguments provided, use non-interactive flows
    if args.json_file or args.identifier:
        cfg = load_config()
        if args.json_file:
            process_mount_list(cfg, args.json_file)
            sys.exit(0)
        if args.identifier:
            title = args.title or args.identifier
            year = args.year
            ok = create_plex_structure(cfg, args.identifier, title, year)
            sys.exit(0 if ok else 1)

    # Fallback to interactive main
    main()
