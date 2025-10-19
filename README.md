# findPublicMedia

A project to find and manage public media resources.

## 🚀 Quick Setup

### 1. Authentication Setup (One-time only)
Run the authentication setup script to securely store your GitHub credentials:
```bash
./scripts/setup-auth.sh
```

This will configure your system to automatically handle GitHub authentication without requiring you to enter your token each time.

### 2. Test Your Setup
After configuring authentication, test it:
```bash
./scripts/test-push.sh
```

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

## 📋 Getting Started

This project is set up with Git flow branching:
- `main` - Production-ready code
- `develop` - Integration branch for features
- Feature branches - Individual features branched off develop

## 🔄 Development Workflow

1. Create feature branches from `develop`
2. Merge completed features back to `develop`
3. When ready for release, merge `develop` to `main`
