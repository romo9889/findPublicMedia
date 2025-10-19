#!/usr/bin/env python3
"""
Tiny Spark: Search TMDB, open a legal Archive.org link.

Usage:
  python vibe_streamer.py               # prompts for a title
  python vibe_streamer.py "Movie Title"
  python vibe_streamer.py --no-open "Movie Title"

Environment:
  TMDB_API_KEY  Your TMDB v3 API key. If missing, we fall back to Archive.org search by your raw query.
    OPENSUBTITLES_API_KEY  Optional. If present, used to query OpenSubtitles API for a direct subtitle page link.
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
OPENSUBTITLES_API_URL = "https://api.opensubtitles.com/api/v1/subtitles"


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


# --- OpenSubtitles helpers ---
_LANG_2_TO_OS3 = {
    # Common mappings to legacy 3-letter codes used by opensubtitles.org search path
    "en": "eng",
    "es": "spa",
    "fr": "fre",  # sometimes 'fra'; 'fre' still supported on site
    "de": "ger",  # sometimes 'deu'; 'ger' still supported on site
    "it": "ita",
    "pt": "por",
    "ru": "rus",
}


def build_opensubtitles_search_url(title: str, lang: str = "en") -> str:
    """Build a public search URL on OpenSubtitles if API is unavailable.

    We use the classic opensubtitles.org search URL form for reliability.
    """
    code = _LANG_2_TO_OS3.get(lang.lower(), _LANG_2_TO_OS3.get("en", "eng"))
    return (
        "https://www.opensubtitles.org/en/search2/"
        f"sublanguageid-{code}/moviename-{urllib.parse.quote(title)}"
    )


def get_subtitle(title: str, lang: str = "en") -> Optional[str]:
    """Search OpenSubtitles and return a direct page URL if available.

    - If OPENSUBTITLES_API_KEY is set, query the OpenSubtitles v1 API and
      return the top result's public URL.
    - Otherwise (or on error/empty results), return a public search URL.
    """
    api_key = os.environ.get("OPENSUBTITLES_API_KEY", "").strip()
    if not api_key:
        return build_opensubtitles_search_url(title, lang)

    try:
        params = {
            "query": title,
            "languages": lang.lower(),
            "type": "movie",
            "order_by": "download_count",
            "order_direction": "desc",
            "page": "1",
        }
        url = f"{OPENSUBTITLES_API_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(
            url,
            headers={
                "Api-Key": api_key,
                "Accept": "application/json",
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        items = data.get("data") or []
        if not items:
            return build_opensubtitles_search_url(title, lang)
        top = items[0]
        attrs = top.get("attributes") or {}
        # New API usually provides a public 'url' under attributes
        url = attrs.get("url")
        if url:
            return url
        return build_opensubtitles_search_url(title, lang)
    except Exception:
        return build_opensubtitles_search_url(title, lang)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Search TMDB and open an Archive.org link for a movie.")
    parser.add_argument("query", nargs="?", help="Movie title to search")
    parser.add_argument("--no-open", action="store_true", help="Don't open a browser; just print the URL")
    parser.add_argument("--subs-lang", default="en", help="Subtitle language (ISO 639-1), default: en")
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

    # Subtitles
    sub_url = get_subtitle(title, args.subs_lang)
    if sub_url:
        print(f"OpenSubtitles URL: {sub_url}")
    else:
        print("OpenSubtitles: No link available.")

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
