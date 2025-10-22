# 📡 Server Setup Guide

This guide helps you copy your Plex library to a server and configure all mount scripts to use it.

## Step 1: Run Server Setup

```bash
python3 setup_server.py
```

This will:
1. Ask for your server configuration
2. Test the connection
3. Copy `~/PlexMovies/` to your server
4. Save configuration for future use

### Supported Server Types

**1. Local/External Drive**
```
Type: local
Example: /Volumes/MyDrive/PlexMovies
```

**2. Network Share (SMB)**
```
Type: smb
Server: //192.168.1.100/Movies
Mount: /Volumes/ServerMovies
```

**3. NAS**
```
Type: nas
Path: /Volumes/Synology/Media/PlexMovies
```

**4. SSH/SFTP Server**
```
Type: ssh
Host: user@server.com
Path: /mnt/media/PlexMovies
```

## Step 2: Verify the Copy

After copying, check your server:

**Local/Network:**
```bash
ls -la /path/to/server/PlexMovies/
```

**SSH Server:**
```bash
ssh user@server "ls -la /mnt/media/PlexMovies/"
```

You should see your movie folders:
```
His Girl Friday (1940)/
Metropolis1927 (1927)/
Gaslight 1944 (1944)/
...
```

## Step 3: Update Mount Scripts

Once verified, update all scripts to use the server:

```bash
python3 update_mount_scripts.py
```

This will:
- Backup original scripts (`.backup` files)
- Update `create_plex_library.py` to use server path
- All future mounts will go to server automatically

## Step 4: Test

Test that new mounts go to the server:

```bash
# This should update files on your server
python3 create_plex_library.py
```

Or mount a new movie:

```bash
python3 vibe_streamer.py "The Great Dictator" --plex
# Should create symlink on server
```

## Checking Configuration

Your server config is saved in: `~/.plex_server_config.json`

View it:
```bash
cat ~/.plex_server_config.json
```

## Troubleshooting

### Connection Failed

**Network share not mounted?**
```bash
# Mount SMB share manually:
mkdir -p /Volumes/ServerMovies
mount_smbfs //user@server/share /Volumes/ServerMovies
```

**SSH key issues?**
```bash
# Test SSH connection:
ssh user@server

# Set up SSH keys if needed:
ssh-copy-id user@server
```

### Copy Failed

**Permission denied?**
- Make sure you have write access to the server path
- Check server user permissions

**Rsync not found?**
```bash
# Install rsync (if needed):
brew install rsync
```

### Server Full?

Check available space:
```bash
df -h /path/to/server
```

The PlexMovies folder is ~42 movies, size varies by quality.

## Reverting to Local

To go back to local storage:

1. Edit `create_plex_library.py`:
   ```python
   PLEX_LIBRARY = Path.home() / "PlexMovies"
   ```

2. Or delete the config and re-run setup:
   ```bash
   rm ~/.plex_server_config.json
   python3 setup_server.py
   ```

## Future Mounts

After setup, everything is automatic:

```bash
# AI batch mount - goes to server
python3 ai_mount_list.py --prompt "western movies"

# Single mount - goes to server
python3 vibe_streamer.py "Casablanca" --plex

# Manual update - syncs to server
python3 create_plex_library.py
```

All commands will automatically:
1. Mount from Archive.org
2. Create clean Plex structure
3. Update server library
4. Ready for Plex to scan
