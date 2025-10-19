#!/usr/bin/env python3
"""
Tiny Spark: Search TMDB, open a legal Archive.org link.

Usage:
  python vibe_streamer.py               # prompts for a title
  python vibe_streamer.py "Movie Title"
  python vibe_streamer.py --no-open "Movie Title"

Environment:
  TMDB_API_KEY  Your TMDB v3 API key. If missing, we fall back to Archive.org search by your raw query.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import webbrowser
from typing import Optional, Tuple

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"


def search_tmdb(query: str, api_key: str) -> Optional[Tuple[str, Optional[int]]]:
    """Return (title, year) for the best-matching movie from TMDB, or None if not found.

    We pick the first result sorted by popularity (TMDB's default) and extract the title and release year.
    """
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
        results = data.get("results") or []
        if not results:
            return None
        top = results[0]
        title = top.get("title") or top.get("name") or query
        release_date = top.get("release_date") or ""
        year = None
        if release_date and len(release_date) >= 4:
            try:
                year = int(release_date[:4])
            except ValueError:
                year = None
        return title, year
    except Exception:
        return None


def build_archive_search_url(title: str, year: Optional[int] = None) -> str:
    """Build a simple Archive.org search URL constrained to movies.

    We use a straightforward full-text search plus mediatype filter for maximum compatibility.
    """
    # Keep it robust and simple. If year is available, include it as free text to bias results.
    terms = title if year is None else f"{title} {year}"
    query = f"{terms} AND mediatype:movies"
    return f"https://archive.org/search?query={urllib.parse.quote_plus(query)}"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Search TMDB and open an Archive.org link for a movie.")
    parser.add_argument("query", nargs="?", help="Movie title to search")
    parser.add_argument("--no-open", action="store_true", help="Don't open a browser; just print the URL")
    args = parser.parse_args(argv)

    query = args.query
    if not query:
        try:
            query = input("Enter movie title: ").strip()
        except EOFError:
            query = ""
    if not query:
        print("No title provided. Exiting.")
        return 1

    api_key = os.environ.get("TMDB_API_KEY", "").strip()

    title: str = query
    year: Optional[int] = None
    if api_key:
        result = search_tmdb(query, api_key)
        if result:
            title, year = result
            print(f"TMDB: Found '{title}'{f' ({year})' if year else ''}")
        else:
            print("TMDB: No results or error; falling back to raw title.")
    else:
        print("TMDB_API_KEY not set; using raw title for Archive.org search.")

    url = build_archive_search_url(title, year)
    print(f"Archive.org search URL: {url}")

    if not args.no_open:
        try:
            opened = webbrowser.open(url)
            if opened:
                print("Opened your default browser.")
            else:
                print("Could not auto-open browser. Paste the URL above into your browser.")
        except webbrowser.Error:
            print("Browser error. Paste the URL into your browser:")
            print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
