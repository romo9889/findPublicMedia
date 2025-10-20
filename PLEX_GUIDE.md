# 📺 Plex Setup Guide for findPublicMedia

Complete guide to streaming Archive.org movies through Plex using findPublicMedia.

---

## 🎯 Overview

This guide will help you:
1. Install required tools (rclone, Plex)
2. Mount Archive.org movies to your Mac
3. Add them to your Plex library
4. Stream directly from Archive.org to any Plex client

**No downloads required!** Movies stream directly from Archive.org.

---

## 📋 Prerequisites

### Step 1: Install rclone

rclone is a tool that mounts remote storage (like Archive.org) as a local folder.

```bash
# macOS
brew install rclone

# Verify installation
rclone version
```

### Step 2: Install Plex Media Server (if not already installed)

**Option A: Download from Plex**
1. Visit https://www.plex.tv/media-server-downloads/
2. Download Plex Media Server for macOS
3. Install and run the installer
4. Complete the initial setup (create account, etc.)

**Option B: Using Homebrew**
```bash
brew install --cask plex-media-server
```

### Step 3: Install macFUSE (Required for mounting on macOS)

macFUSE allows rclone to mount remote filesystems on macOS.

```bash
brew install --cask macfuse
```

**Important:** After installing macFUSE, you need to:
1. Go to **System Settings** → **Privacy & Security**
2. Scroll down and click **Allow** next to the macFUSE system extension
3. **Restart your Mac** for changes to take effect

---

## 🚀 Quick Start: Mount Your First Movie

### Method 1: Using findPublicMedia (Easiest)

Search for a movie and mount it automatically:

```bash
python3 vibe_streamer.py "His Girl Friday" --plex
```

This will:
- Search TMDB for the movie
- Find the Archive.org item
- Set up rclone configuration
- Mount to `~/ArchiveMount/HisGirlFriday1940`
- Print next steps for Plex

### Method 2: Direct Link (if you know the Archive.org URL)

```bash
python3 stream_now.py --ia-link "https://archive.org/details/HisGirlFriday1940" --mode plex
```

---

## 📂 Adding Mounted Movies to Plex

### Step 1: Open Plex Web Interface

1. Open your browser and go to: http://localhost:32400/web
2. Sign in to your Plex account

### Step 2: Create a New Library

1. Click on **Settings** (wrench icon in top right)
2. Select **Manage** → **Libraries**
3. Click **+ Add Library**
4. Choose **Movies**
5. Click **Next**

### Step 3: Add Folder(s)

1. Click **Add Folder**
2. Navigate to: `/Users/YOUR_USERNAME/ArchiveMount`
3. You'll see folders for each mounted Archive.org item:
   ```
   ArchiveMount/
   ├── HisGirlFriday1940/
   ├── NightOfTheLivingDead-MPEG/
   └── Charade_201712/
   ```
4. Select **one or more** item folders (or select the whole `ArchiveMount` folder)
5. Click **Add**

### Step 4: Configure Library Settings

Recommended settings:
- **Scanner:** Plex Movie Scanner
- **Agent:** Plex Movie (or The Movie Database)
- **Enable video preview thumbnails:** ON
- **Include in dashboard:** ON
- **Enable Cinema Trailers:** OFF (optional)

Click **Add Library**

### Step 5: Wait for Scan

Plex will scan and identify the movies. This usually takes 30-60 seconds.

---

## 🎬 Mounting Multiple Movies

### Add Individual Movies

```bash
# Mount multiple movies one by one
python3 vibe_streamer.py "Night of the Living Dead" --plex
python3 vibe_streamer.py "Charade" --plex
python3 vibe_streamer.py "The General" --plex
```

Each movie gets its own folder in `~/ArchiveMount/`.

### Create a Movie Collection

After mounting several movies, they all appear in your single Plex Movies library:

```
Plex Library: Public Domain Movies
├── His Girl Friday (1940)
├── Night of the Living Dead (1968)
├── Charade (1963)
├── The General (1926)
└── ...
```

---

## 🔧 Managing Mounts

### List All Active Mounts

```bash
python3 mount_archive.py list
```

Output:
```
Active Archive.org mounts:
  - HisGirlFriday1940 → /Users/rosa/ArchiveMount/HisGirlFriday1940
  - NightOfTheLivingDead-MPEG → /Users/rosa/ArchiveMount/NightOfTheLivingDead-MPEG
```

### Unmount a Specific Movie

```bash
python3 mount_archive.py unmount HisGirlFriday1940
```

**Note:** After unmounting, the movie will disappear from Plex. Remount it to restore access.

### Unmount All Movies

```bash
python3 mount_archive.py unmount-all
```

---

## 🔄 Auto-Mount on Startup (Optional)

To keep your Archive.org movies available after restarting your Mac:

### Method 1: Create a Launch Agent (Recommended)

Create a file: `~/Library/LaunchAgents/com.findpublicmedia.automount.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.findpublicmedia.automount</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>
        cd /Users/YOUR_USERNAME/Projects/findPublicMedia
        python3 vibe_streamer.py "His Girl Friday" --plex
        python3 vibe_streamer.py "Night of the Living Dead" --plex
        </string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
```

Replace `YOUR_USERNAME` and add your favorite movies.

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.findpublicmedia.automount.plist
```

### Method 2: Simple Shell Script

Create `~/mount-my-movies.sh`:

```bash
#!/bin/bash
cd ~/Projects/findPublicMedia

python3 vibe_streamer.py "His Girl Friday" --plex
python3 vibe_streamer.py "Night of the Living Dead" --plex
python3 vibe_streamer.py "Charade" --plex

echo "✅ All movies mounted!"
```

Make it executable:
```bash
chmod +x ~/mount-my-movies.sh
```

Run it whenever you restart:
```bash
~/mount-my-movies.sh
```

---

## 🎯 Finding More Movies

### Browse Archive.org Public Domain Movies

1. Visit: https://archive.org/details/feature_films
2. Look for movies marked as "Public Domain"
3. Copy the Archive.org URL (e.g., `https://archive.org/details/IDENTIFIER`)
4. Mount it:
   ```bash
   python3 stream_now.py --ia-link "PASTE_URL_HERE" --mode plex
   ```

### Popular Public Domain Films on Archive.org

```bash
# Classic Horror
python3 stream_now.py --ia-link "https://archive.org/details/NightOfTheLivingDead-MPEG" --mode plex

# Classic Comedy
python3 stream_now.py --ia-link "https://archive.org/details/HisGirlFriday1940" --mode plex

# Classic Thriller
python3 stream_now.py --ia-link "https://archive.org/details/Charade_201712" --mode plex

# Silent Era
python3 stream_now.py --ia-link "https://archive.org/details/The_General_Buster_Keaton" --mode plex

# Film Noir
python3 stream_now.py --ia-link "https://archive.org/details/D.O.A.1950" --mode plex
```

---

## 🎬 Streaming from Plex

Once mounted and added to Plex, you can stream from:

**Devices:**
- ✅ Mac/PC (Plex app or web browser)
- ✅ iPhone/iPad (Plex app)
- ✅ Apple TV (Plex app)
- ✅ Roku, Fire TV, Samsung TV, LG TV (Plex apps)
- ✅ Game consoles (PS5, Xbox)
- ✅ Android phones/tablets

**Anywhere:**
- Home network: Direct streaming
- Remote: Enable Plex Remote Access in Settings

---

## ⚠️ Troubleshooting

### "Mount failed" or "rclone: command not found"

**Solution:** Install rclone
```bash
brew install rclone
```

### "macFUSE not found" or "mount: no file system for macfuse"

**Solution:** Install and enable macFUSE
```bash
brew install --cask macfuse
```
Then:
1. Go to System Settings → Privacy & Security
2. Allow the macFUSE extension
3. Restart your Mac

### Movies not showing up in Plex

**Solution 1:** Scan library manually
1. In Plex, go to your Movies library
2. Click the **...** menu → **Scan Library Files**

**Solution 2:** Check mount is active
```bash
python3 mount_archive.py list
```

If no mounts shown, remount the movie.

### Playback buffering or stuttering

**Cause:** Network speed or Archive.org server load

**Solutions:**
- Wait a few seconds for buffer to fill
- Try a different Archive.org item (some have faster servers)
- Lower video quality in Plex playback settings

### Can't unmount

```bash
# Force unmount (macOS)
sudo umount -f ~/ArchiveMount/IDENTIFIER

# Or use fusermount
fusermount -u ~/ArchiveMount/IDENTIFIER
```

---

## 🎓 Tips & Best Practices

### Tip 1: Organize by Collection

In Plex, create Collections for themes:
- "Public Domain Classics"
- "Film Noir Collection"
- "Silent Films"
- "Classic Horror"

### Tip 2: Use Quality Metadata

Plex will auto-match most classic films. If not:
- Right-click movie → **Match**
- Search manually by title + year
- Select correct match from TMDB

### Tip 3: Keep Mounts Minimal

Only mount movies you actively watch. Unmount others to reduce resource usage:
```bash
python3 mount_archive.py unmount IDENTIFIER
```

### Tip 4: Backup Your Mount List

Save your favorite Archive.org URLs in a text file for easy remounting:

`my-movies.txt`:
```
https://archive.org/details/HisGirlFriday1940
https://archive.org/details/NightOfTheLivingDead-MPEG
https://archive.org/details/Charade_201712
```

---

## ✅ You're All Set!

You now have a fully functional Plex library streaming public domain movies from Archive.org.

### Quick Reference

```bash
# Mount a movie
python3 vibe_streamer.py "Movie Title" --plex

# List mounts
python3 mount_archive.py list

# Unmount
python3 mount_archive.py unmount IDENTIFIER

# Stream in VLC instead
python3 vibe_streamer.py "Movie Title" --stream
```

**Enjoy your legal, free movie streaming! 🎬🍿**
