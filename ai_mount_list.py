#!/usr/bin/env python3
"""
AI-Powered Mount List Creator

Interactive script that:
1. Prompts user for a natural language movie description
2. Uses TMDB/Archive.org search to find matching films
3. Presents a list of up to 20 candidates
4. Mounts them one by one using rclone for Plex/Jellyfin

Usage:
  python ai_mount_list.py
  python ai_mount_list.py --prompt "classic noir films from the 1940s"
  python ai_mount_list.py --limit 10 --prompt "sci-fi about AI"

Environment:
  TMDB_API_KEY  Your TMDB v3 API key (recommended for better search results)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

# Import from our existing modules
try:
    from vibe_streamer import archive_search_candidates, pick_best_archive_item, search_tmdb
except ImportError:
    print("Error: Could not import from vibe_streamer.py")
    print("Make sure vibe_streamer.py is in the same directory.")
    sys.exit(1)

try:
    from stream_now import extract_identifier, fetch_metadata
except ImportError:
    print("Error: Could not import from stream_now.py")
    print("Make sure stream_now.py is in the same directory.")
    sys.exit(1)


TMDB_DISCOVER_URL = "https://api.themoviedb.org/3/discover/movie"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
ARCHIVE_ADV_SEARCH = "https://archive.org/advancedsearch.php"
ARCHIVE_DOWNLOAD_URL = "https://archive.org/download/"


def create_collection_name(prompt: str) -> str:
    """
    Create a descriptive, filesystem-safe folder name from the user's prompt.
    
    Examples:
    - "classic film noir from the 1940s" -> "classic_film_noir_1940s"
    - "sci-fi movies about AI" -> "scifi_movies_ai"
    - "hitchcock thrillers" -> "hitchcock_thrillers"
    """
    # Remove common filler words
    filler_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'from', 'about', 'movies', 'films', 'movie', 'film'
    }
    
    # Convert to lowercase and split into words
    words = prompt.lower().split()
    
    # Filter out filler words and keep meaningful terms
    meaningful_words = [w for w in words if w not in filler_words]
    
    # If we filtered everything, fall back to original
    if not meaningful_words:
        meaningful_words = words
    
    # Take first 4-5 meaningful words to keep name reasonable
    selected_words = meaningful_words[:5]
    
    # Clean each word: remove punctuation, make filesystem-safe
    cleaned_words = []
    for word in selected_words:
        # Remove non-alphanumeric chars except hyphens
        cleaned = ''.join(c if c.isalnum() or c == '-' else '' for c in word)
        if cleaned:
            cleaned_words.append(cleaned)
    
    # Join with underscores
    collection_name = '_'.join(cleaned_words)
    
    # Limit total length to 50 chars
    if len(collection_name) > 50:
        collection_name = collection_name[:50].rstrip('_')
    
    # If empty after cleaning, use a default
    if not collection_name:
        collection_name = "movie_collection"
    
    return collection_name


def mount_archive_item(identifier: str, mount_path: Path) -> bool:
    """
    Mount a single Archive.org item using rclone.
    Returns True on success, False on failure.
    """
    try:
        # Check if rclone is installed
        subprocess.run(["rclone", "version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ rclone not found. Please install it first.")
        return False
    
    # Create mount point
    mount_path.mkdir(parents=True, exist_ok=True)
    
    # Extract base URL for the item
    base_url = f"{ARCHIVE_DOWNLOAD_URL}{urllib.parse.quote(identifier)}/"
    
    # Create rclone config for this mount
    config_name = f"archive_{identifier.replace('-', '_')[:50]}"
    
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
    
    if f"[{config_name}]" not in existing_config:
        with open(rclone_config_file, "a") as f:
            f.write("\n" + config_content)
    
    # Mount command
    mount_cmd = [
        "rclone", "mount",
        f"{config_name}:", str(mount_path),
        "--read-only",
        "--vfs-cache-mode", "full",
        "--daemon"
    ]
    
    try:
        subprocess.run(mount_cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  rclone mount failed: {e.stderr.decode() if e.stderr else str(e)}")
        return False


def print_banner():
    """Print a welcome banner."""
    print("\n" + "="*60)
    print("🎬  AI-POWERED MOVIE MOUNT LIST CREATOR  🎬")
    print("="*60)
    print("Describe the movies you want and I'll find & mount them!\n")


def get_user_prompt() -> str:
    """Get natural language movie description from user."""
    print("📝 Describe the movies you're looking for:")
    print("   Examples:")
    print("   - 'classic film noir from the 1940s'")
    print("   - 'sci-fi movies about artificial intelligence'")
    print("   - 'comedies from the silent era'")
    print("   - 'hitchcock thrillers'")
    print()
    prompt = input("Your description: ").strip()
    if not prompt:
        print("❌ No prompt provided. Exiting.")
        sys.exit(1)
    return prompt


def search_movies_by_description(prompt: str, limit: int = 20) -> list:
    """
    Search for movies matching the user's natural language description.
    
    Strategy:
    1. Try TMDB search first (if API key available)
    2. Fall back to Archive.org advanced search
    3. Return list of movie metadata dicts
    """
    results = []
    api_key = os.environ.get("TMDB_API_KEY", "").strip()
    
    print(f"\n🔍 Searching for movies matching: '{prompt}'...")
    
    # Strategy 1: Use TMDB search for popular results
    if api_key:
        results.extend(_search_tmdb_multiple(prompt, api_key, limit))
    
    # Strategy 2: Search Archive.org directly with the prompt
    if len(results) < limit:
        results.extend(_search_archive_direct(prompt, limit - len(results)))
    
    # Deduplicate by title (case-insensitive)
    seen = set()
    unique_results = []
    for r in results:
        title_key = r.get("title", "").lower().strip()
        if title_key and title_key not in seen:
            seen.add(title_key)
            unique_results.append(r)
    
    return unique_results[:limit]


def _search_tmdb_multiple(query: str, api_key: str, limit: int = 20) -> list:
    """Search TMDB and return multiple results."""
    try:
        params = {
            "api_key": api_key,
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": "1",
        }
        url = f"{TMDB_SEARCH_URL}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
        
        results = []
        for movie in (data.get("results") or [])[:limit]:
            title = movie.get("title") or movie.get("name")
            release_date = movie.get("release_date") or ""
            year = None
            if release_date and len(release_date) >= 4:
                try:
                    year = int(release_date[:4])
                except ValueError:
                    pass
            
            if title:
                results.append({
                    "title": title,
                    "year": year,
                    "source": "tmdb",
                })
        
        return results
    except Exception as e:
        print(f"⚠️  TMDB search failed: {e}")
        return []


def _search_archive_direct(query: str, limit: int = 20) -> list:
    """Search Archive.org directly with the user's prompt."""
    try:
        # Use advanced search with the full prompt
        terms = f'({query}) AND mediatype:(movies)'
        params = {
            "q": terms,
            "fl[]": ["identifier", "title", "year"],
            "sort[]": ["downloads desc", "date desc"],
            "rows": limit,
            "output": "json",
        }
        url = f"{ARCHIVE_ADV_SEARCH}?{urllib.parse.urlencode(params, doseq=True)}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.load(resp)
        
        docs = (((data or {}).get("response") or {}).get("docs") or [])
        results = []
        for doc in docs:
            if doc.get("identifier"):
                results.append({
                    "title": doc.get("title", "Unknown Title"),
                    "year": doc.get("year"),
                    "identifier": doc.get("identifier"),
                    "source": "archive",
                })
        
        return results
    except Exception as e:
        print(f"⚠️  Archive.org search failed: {e}")
        return []


def resolve_archive_identifiers(movies: list) -> list:
    """
    For movies without Archive.org identifiers, search for them.
    Returns list of movies with identifiers.
    """
    resolved = []
    
    for movie in movies:
        if movie.get("identifier"):
            # Already has identifier
            resolved.append(movie)
        else:
            # Need to search Archive.org
            title = movie.get("title")
            year = movie.get("year")
            
            print(f"  🔎 Searching Archive.org for: {title} ({year or 'unknown year'})")
            candidates = archive_search_candidates(title, year, rows=5)
            
            if candidates:
                identifier = pick_best_archive_item(candidates, title)
                if identifier:
                    movie["identifier"] = identifier
                    resolved.append(movie)
                else:
                    print(f"     ❌ No suitable item found")
            else:
                print(f"     ❌ No results found")
    
    return resolved


def display_results(movies: list):
    """Display the found movies in a nice table."""
    print(f"\n✨ Found {len(movies)} movies:\n")
    print(f"{'#':<4} {'Title':<50} {'Year':<6} {'Identifier':<30}")
    print("-" * 90)
    
    for idx, movie in enumerate(movies, 1):
        title = movie.get("title", "Unknown")[:48]
        year = str(movie.get("year") or "")[:4]
        identifier = movie.get("identifier", "N/A")[:28]
        print(f"{idx:<4} {title:<50} {year:<6} {identifier:<30}")
    
    print()


def confirm_mount(count: int) -> bool:
    """Ask user to confirm mounting."""
    response = input(f"\n🚀 Mount all {count} movies? (y/n): ").strip().lower()
    return response in ("y", "yes")


def mount_movies(movies: list, mount_base: Path) -> dict:
    """
    Mount each movie one by one.
    Returns dict with success/failure counts and details.
    """
    results = {
        "total": len(movies),
        "mounted": 0,
        "failed": 0,
        "skipped": 0,
        "details": [],
    }
    
    mount_base.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📂 Mount base directory: {mount_base}")
    print(f"\n🔄 Starting batch mount process...\n")
    
    for idx, movie in enumerate(movies, 1):
        title = movie.get("title", "Unknown")
        identifier = movie.get("identifier")
        
        if not identifier:
            print(f"[{idx}/{results['total']}] ⏭️  Skipping '{title}' (no identifier)")
            results["skipped"] += 1
            results["details"].append({
                "title": title,
                "status": "skipped",
                "reason": "no identifier",
            })
            continue
        
        print(f"[{idx}/{results['total']}] 🎬 Mounting: {title}")
        print(f"              ID: {identifier}")
        
        try:
            # Check if already mounted
            mount_path = mount_base / identifier
            if mount_path.exists() and list(mount_path.iterdir()):
                print(f"              ✅ Already mounted at {mount_path}")
                results["mounted"] += 1
                results["details"].append({
                    "title": title,
                    "identifier": identifier,
                    "status": "already_mounted",
                    "path": str(mount_path),
                })
                continue
            
            # Fetch metadata to verify item exists
            print(f"              ⏳ Fetching metadata...")
            metadata = fetch_metadata(identifier)
            
            if not metadata:
                print(f"              ❌ Failed to fetch metadata")
                results["failed"] += 1
                results["details"].append({
                    "title": title,
                    "identifier": identifier,
                    "status": "failed",
                    "reason": "metadata fetch failed",
                })
                continue
            
            # Attempt mount
            print(f"              ⏳ Mounting via rclone...")
            success = mount_archive_item(identifier, mount_path)
            
            if not success:
                print(f"              ❌ Mount command failed")
                results["failed"] += 1
                results["details"].append({
                    "title": title,
                    "identifier": identifier,
                    "status": "failed",
                    "reason": "rclone mount failed",
                })
                continue
            
            # Verify mount succeeded by checking if directory has contents
            time.sleep(2)  # Give mount a moment to initialize
            
            if mount_path.exists() and any(mount_path.iterdir()):
                print(f"              ✅ Successfully mounted to {mount_path}")
                results["mounted"] += 1
                results["details"].append({
                    "title": title,
                    "identifier": identifier,
                    "status": "mounted",
                    "path": str(mount_path),
                })
            else:
                print(f"              ⚠️  Mount directory empty or failed")
                results["failed"] += 1
                results["details"].append({
                    "title": title,
                    "identifier": identifier,
                    "status": "failed",
                    "reason": "mount verification failed",
                })
        
        except Exception as e:
            print(f"              ❌ Error: {e}")
            results["failed"] += 1
            results["details"].append({
                "title": title,
                "identifier": identifier,
                "status": "failed",
                "reason": str(e),
            })
        
        print()
        
        # Small delay between mounts
        if idx < results["total"]:
            time.sleep(1)
    
    return results


def update_plex_library():
    """Run the Plex library organizer to update symlinks."""
    try:
        print("\n🔄 Updating Plex library...")
        result = subprocess.run(
            [sys.executable, "create_plex_library.py"],
            check=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        print("✅ Plex library updated!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Plex library update failed")
        return False
    except FileNotFoundError:
        print("⚠️  create_plex_library.py not found - skipping Plex update")
        return False


def print_summary(results: dict, collection_path: Path = None):
    """Print final summary of mount operation."""
    print("\n" + "="*60)
    print("📊 MOUNT SUMMARY")
    print("="*60)
    print(f"Total movies:     {results['total']}")
    print(f"✅ Mounted:       {results['mounted']}")
    print(f"❌ Failed:        {results['failed']}")
    print(f"⏭️  Skipped:       {results['skipped']}")
    print("="*60)
    
    if results["mounted"] > 0:
        print("\n🎉 Successfully mounted movies are ready for Plex/Jellyfin!")
        if collection_path:
            print(f"� Collection path: {collection_path}")
        print("�💡 Add the collection directory to your Plex library to see them.")


def main(argv: list[str]) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered movie search and mount tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--prompt",
        help="Natural language movie description (interactive if not provided)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of movies to find (default: 20)",
    )
    parser.add_argument(
        "--mount-base",
        default=str(Path.home() / "ArchiveMount"),
        help="Base directory for mounts (default: ~/ArchiveMount)",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt and mount immediately",
    )
    
    args = parser.parse_args(argv[1:])
    
    # Banner
    print_banner()
    
    # Get prompt
    prompt = args.prompt
    if not prompt:
        prompt = get_user_prompt()
    else:
        print(f"📝 Using prompt: {prompt}\n")
    
    # Search for movies
    movies = search_movies_by_description(prompt, args.limit)
    
    if not movies:
        print("\n❌ No movies found matching your description.")
        print("💡 Try a different search query or check your TMDB_API_KEY")
        return 1
    
    # Resolve Archive.org identifiers
    print(f"\n🔗 Resolving Archive.org identifiers...")
    movies = resolve_archive_identifiers(movies)
    
    if not movies:
        print("\n❌ No movies could be found on Archive.org.")
        return 1
    
    # Display results
    display_results(movies)
    
    # Confirm
    if not args.yes:
        if not confirm_mount(len(movies)):
            print("❌ Mount cancelled by user.")
            return 0
    
    # Create collection-specific subfolder
    collection_name = create_collection_name(prompt)
    mount_base = Path(args.mount_base) / collection_name
    
    print(f"\n📁 Collection: '{collection_name}'")
    
    # Mount movies
    results = mount_movies(movies, mount_base)
    
    # Update Plex library
    if results["mounted"] > 0:
        update_plex_library()
    
    # Summary
    print_summary(results, mount_base)
    
    # Save results to JSON
    results["collection_name"] = collection_name
    results["collection_path"] = str(mount_base)
    results["prompt"] = prompt
    results_file = Path("mount_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return 0 if results["mounted"] > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
