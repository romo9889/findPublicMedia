#!/usr/bin/env python3
"""
Create a clean Plex-friendly movie library from Archive.org mounts.

This script:
1. Scans Archive.org mount directories
2. Identifies the best quality video file for each movie
3. Creates a Plex-friendly structure with symlinks
4. Excludes duplicates, thumbnails, and metadata files
"""
from pathlib import Path
import re
import json
from typing import Optional, Tuple
import subprocess

MOUNT_BASE = Path.home() / "ArchiveMount"
PLEX_LIBRARY = Path.home() / "PlexMovies"

# Video quality priority (higher is better)
VIDEO_FORMATS = {
    '.mp4': 10,
    '.mkv': 9,
    '.avi': 8,
    '.mov': 7,
    '.mpeg': 6,
    '.mpg': 5,
    '.ogv': 4,
    '.webm': 3,
}

# Files to exclude
EXCLUDE_PATTERNS = [
    r'\.thumbs$',
    r'_512kb\.',
    r'_archive\.torrent$',
    r'_files\.xml$',
    r'_meta\.xml$',
    r'_reviews\.xml$',
    r'__ia_thumb\.',
    r'\.gif$',
    r'\.png$',
    r'\.jpg$',
    r'\.jpeg$',
    r'\.torrent$',
    r'\.xml$',
    r'\.js$',
]


def should_exclude(filename: str) -> bool:
    """Check if file should be excluded."""
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
    return False


def extract_year(identifier: str, metadata_file: Path = None) -> Optional[int]:
    """Try to extract year from identifier or metadata."""
    # Try identifier first
    year_match = re.search(r'(19\d{2}|20\d{2})', identifier)
    if year_match:
        return int(year_match.group(1))
    
    # Try metadata file if available
    if metadata_file and metadata_file.exists():
        try:
            with open(metadata_file) as f:
                for line in f:
                    if 'year' in line.lower():
                        year_match = re.search(r'(19\d{2}|20\d{2})', line)
                        if year_match:
                            return int(year_match.group(1))
        except:
            pass
    
    return None


def clean_movie_name(identifier: str) -> str:
    """Clean up movie name from Archive.org identifier."""
    # Remove common suffixes
    name = identifier
    name = re.sub(r'_\d{6,}$', '', name)  # Remove long number suffixes
    name = re.sub(r'_202\d{3}$', '', name)  # Remove date suffixes
    name = re.sub(r'EnglishVersion$', '', name, re.IGNORECASE)
    name = re.sub(r'_most_complete_version.*$', '', name)
    name = re.sub(r'TheCabinetofDr', 'The Cabinet of Dr ', name)
    
    # Replace underscores and hyphens with spaces
    name = name.replace('_', ' ').replace('-', ' ')
    
    # Clean up multiple spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Title case
    name = name.title()
    
    return name


def find_best_video(mount_path: Path) -> Optional[Path]:
    """Find the best quality video file in the mount."""
    best_video = None
    best_score = -1
    
    for file in mount_path.iterdir():
        if file.is_dir():
            continue
        
        if should_exclude(file.name):
            continue
        
        ext = file.suffix.lower()
        if ext not in VIDEO_FORMATS:
            continue
        
        # Skip low quality versions
        if '512kb' in file.name.lower():
            continue
        
        # Calculate score based on extension and file size
        score = VIDEO_FORMATS.get(ext, 0)
        
        # Prefer files without quality indicators in name
        if 'hd' in file.name.lower() or '1080' in file.name or '720' in file.name:
            score += 5
        
        if score > best_score:
            best_score = score
            best_video = file
    
    return best_video


def find_subtitle(mount_path: Path, video_name: str) -> Optional[Path]:
    """Find subtitle file for the video."""
    base_name = Path(video_name).stem
    
    for file in mount_path.iterdir():
        if file.suffix.lower() in ['.srt', '.vtt', '.sub']:
            # Prefer .srt files
            if file.suffix.lower() == '.srt':
                return file
    
    return None


def create_plex_structure():
    """Create clean Plex library structure from Archive.org mounts."""
    print(f"🎬 Creating Plex-friendly library at: {PLEX_LIBRARY}\n")
    
    PLEX_LIBRARY.mkdir(parents=True, exist_ok=True)
    
    # Collect all movie mounts
    movies_processed = 0
    movies_skipped = 0
    
    for collection_dir in MOUNT_BASE.iterdir():
        if not collection_dir.is_dir():
            continue
        
        # Skip if it's not a collection folder
        if collection_dir.name.startswith('.'):
            continue
        
        print(f"📂 Processing collection: {collection_dir.name}")
        
        for movie_mount in collection_dir.iterdir():
            if not movie_mount.is_dir():
                continue
            
            identifier = movie_mount.name
            
            # Find best video
            video_file = find_best_video(movie_mount)
            if not video_file:
                print(f"  ⚠️  No video found for: {identifier}")
                movies_skipped += 1
                continue
            
            # Extract year and clean name
            year = extract_year(identifier, movie_mount / f"{identifier}_meta.xml")
            clean_name = clean_movie_name(identifier)
            
            # Create Plex folder name
            if year:
                folder_name = f"{clean_name} ({year})"
            else:
                folder_name = clean_name
            
            # Create movie folder in Plex library
            movie_folder = PLEX_LIBRARY / folder_name
            movie_folder.mkdir(parents=True, exist_ok=True)
            
            # Create symlink for video
            video_link = movie_folder / f"{folder_name}{video_file.suffix}"
            if video_link.exists():
                video_link.unlink()
            video_link.symlink_to(video_file)
            
            # Create symlink for subtitle if exists
            subtitle = find_subtitle(movie_mount, video_file.name)
            if subtitle:
                sub_link = movie_folder / f"{folder_name}{subtitle.suffix}"
                if sub_link.exists():
                    sub_link.unlink()
                sub_link.symlink_to(subtitle)
            
            print(f"  ✅ {folder_name}")
            movies_processed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Summary")
    print(f"{'='*60}")
    print(f"Movies organized: {movies_processed}")
    print(f"Movies skipped:   {movies_skipped}")
    print(f"\n📁 Plex library: {PLEX_LIBRARY}")
    print(f"\n💡 Next steps:")
    print(f"   1. Open Plex Web")
    print(f"   2. Add Library → Movies")
    print(f"   3. Point to: {PLEX_LIBRARY}")
    print(f"   4. Use 'Plex Movie' scanner")
    print(f"   5. Scan and enjoy!")


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("🎬 PLEX LIBRARY ORGANIZER")
    print("="*60)
    print("Creating clean, Plex-friendly movie library...")
    print("Excludes: duplicates, thumbnails, low-quality versions\n")
    
    create_plex_structure()


if __name__ == "__main__":
    main()
