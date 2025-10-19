# findPublicMedia

A project to find and manage public media resources.

## 🩵 Step 1 — The Tiny Spark

Goal: Search for a movie and open a legal link in your browser.

### 1) Get a free TMDB API key
- Create an account at https://www.themoviedb.org/
- Go to your account settings → API → Request an API key (v3)
- Copy the key

In your terminal (zsh), set it for this session:

```zsh
export TMDB_API_KEY="YOUR_TMDB_V3_API_KEY"
```

Optional: add that line to your `~/.zshrc` to persist it across sessions.

### 2) Run the tiny app
From the repo root in VS Code’s terminal:

```zsh
python3 vibe_streamer.py
```

When prompted, type:

```
Night of the Living Dead
```

It will open an Archive.org search page for that film in your default browser.

Tip: you can also run without a key (it will still open an Archive.org search by raw title),
but the TMDB key improves title/year matching.

## 🧩 Step 2 — Subtitles (Optional)

Add a function to retrieve a subtitle link from OpenSubtitles.

### 1) Optional: OpenSubtitles API key
You can use the public site without a key, or provide an API key for better results.

```zsh
export OPENSUBTITLES_API_KEY="YOUR_OS_API_KEY"
```

### 2) Run with a language code
Default language is English (`en`). You can change it, for example Spanish (`es`):

```zsh
python3 vibe_streamer.py --no-open --subs-lang es "Night of the Living Dead"
```

You will see two links printed:
- Archive.org search URL
- OpenSubtitles URL (direct API result if key provided; otherwise a site search link)

## Getting Started

This project is set up with Git flow branching:
- `main` - Production-ready code
- `develop` - Integration branch for features
- Feature branches - Individual features branched off develop

## Development Workflow

1. Create feature branches from `develop`
2. Merge completed features back to `develop`
3. When ready for release, merge `develop` to `main`