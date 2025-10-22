# Server Setup Security Guide

## 🔒 Security Best Practices

This project is **public on GitHub**, so we follow strict security practices:

### What's NEVER Stored in Git
- ❌ Server IP addresses
- ❌ SSH credentials
- ❌ Passwords
- ❌ API keys
- ❌ Any server configuration

### Where Credentials Are Stored
All sensitive data is stored **locally only**:
- `~/.plex_server_config.json` - Server configuration (gitignored)
- File permissions: `600` (user read/write only)

### Protected by .gitignore
```
*server_config.json
*_config.json
*.token
*.key
*.pem
.credentials
```

## 🌐 Multi-Project Server Setup

Your server can host multiple projects simultaneously:

```
Your Server
├── Shop (existing)
├── n8n (planned)
└── PlexMovies/ (this project)
    └── [organized movie folders]
```

### How It Works
1. **Isolated directories**: Each project has its own path
2. **SSH access**: Secure file transfer using SSH/rsync
3. **No conflicts**: Projects don't interfere with each other

## 📋 Setup Process

### 1. Run Server Setup
```bash
python3 setup_server.py
```

The script will ask you interactively:
- Server IP address
- SSH username
- SSH port (default: 22)
- Remote path for movies (e.g., `/home/user/PlexMovies`)

### 2. Authentication Options

**Recommended: SSH Key** (most secure)
```bash
# Generate key if you don't have one
ssh-keygen -t ed25519

# Copy to your server
ssh-copy-id -p 22 user@your-server-ip
```

**Alternative: Password**
- You'll be prompted during file copy
- Not stored anywhere
- Less convenient but works

### 3. What Happens
1. ✅ Tests SSH connection
2. ✅ Creates remote directory
3. ✅ Copies your Plex library (follows symlinks to copy actual files)
4. ✅ Saves config to `~/.plex_server_config.json` (local only)

### 4. After Setup
- Files are on your server
- Local config saved for future use
- No credentials in git
- Run `update_mount_scripts.py` to update scripts for server mounting

## 🔐 SSH Key Setup (Recommended)

### Why SSH Keys?
- ✓ More secure than passwords
- ✓ No typing passwords repeatedly
- ✓ Can be password-protected
- ✓ Industry standard

### Quick Setup
```bash
# 1. Generate key (if needed)
ssh-keygen -t ed25519 -C "plex-setup"

# 2. Copy to server
ssh-copy-id -p 22 username@server-ip

# 3. Test connection
ssh -p 22 username@server-ip
```

## 🚨 If You Accidentally Commit Credentials

If you accidentally commit a config file with credentials:

1. **Remove from git history**:
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .plex_server_config.json" \
  --prune-empty --tag-name-filter cat -- --all
```

2. **Force push** (⚠️ use with caution):
```bash
git push origin --force --all
```

3. **Change your credentials** on the server immediately

## ✅ Security Checklist

Before running setup:
- [ ] Ensure `.gitignore` includes `*server_config.json`
- [ ] Never commit files with credentials
- [ ] Use SSH keys instead of passwords when possible
- [ ] Set file permissions to 600 for config files
- [ ] Keep server software updated
- [ ] Use strong passwords/passphrases

## 📞 Server Configuration Examples

### Example 1: Shared Hosting Server
```
IP: 192.168.1.100
Port: 22
User: myuser
Path: /home/myuser/PlexMovies
```

### Example 2: VPS/Cloud Server
```
IP: your-server.com
Port: 22
User: root
Path: /var/media/PlexMovies
```

### Example 3: Custom SSH Port
```
IP: 192.168.1.50
Port: 2222
User: mediauser
Path: /mnt/storage/PlexMovies
```

## 🆘 Troubleshooting

### "Connection refused"
- Check if SSH is running: `systemctl status sshd`
- Verify firewall allows SSH: `sudo ufw status`
- Try manual SSH: `ssh -p 22 user@server-ip`

### "Permission denied"
- Check SSH key is copied: `ssh-copy-id -p 22 user@server-ip`
- Verify directory permissions on server
- Try with password authentication first

### "Directory creation failed"
- SSH to server and create manually: `mkdir -p /path/to/PlexMovies`
- Check disk space: `df -h`
- Verify write permissions: `ls -la /parent/directory`

## 📚 Additional Resources

- [SSH Key Authentication Guide](https://www.ssh.com/academy/ssh/keygen)
- [Rsync Manual](https://linux.die.net/man/1/rsync)
- [Plex Server Setup](https://support.plex.tv/)
