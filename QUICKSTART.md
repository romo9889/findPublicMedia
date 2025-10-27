# 🚀 Quick Reference - Production Deployment

## Your Server Info
- **IP**: 138.199.161.86
- **User**: root
- **Plex Path**: /home/root/PlexMovies

## 🎯 Deploy Now (Simple)

SSH to your server and run:

```bash
sudo bash -c "$(wget -qO- https://raw.githubusercontent.com/romo9889/findPublicMedia/main/deployment/setup.sh)"
```

This will:
- ✅ Install all dependencies
- ✅ Clone the repository to `/opt/findPublicMedia`
- ✅ Set up Python packages
- ✅ Generate secure SECRET_KEY
- ✅ Configure systemd service
- ✅ Optionally set up Nginx + SSL

## 🔐 First Login

After deployment:
1. Access: `http://YOUR_IP:5001` (or your domain if you set up Nginx)
2. Login with: **admin** / **changeme**
3. **IMMEDIATELY** change password in `/opt/findPublicMedia/users.json`

## 🎬 How to Use

1. **Login** → Enter credentials
2. **Configure Server** → Click "Configure Server" button, enter your Plex server details
3. **Search Movies** → Enter movie name or prompt (e.g., "sci-fi action movies")
4. **Select Movies** → Check the movies you want to mount
5. **Mount** → Click "Mount Selected Movies"
6. **Watch Progress** → See real-time progress bar and log

## 🔧 Common Commands

```bash
# Check service status
sudo systemctl status plex-mounter

# View live logs
sudo journalctl -u plex-mounter -f

# Restart service
sudo systemctl restart plex-mounter

# Stop service
sudo systemctl stop plex-mounter

# Update to latest version
cd /opt/findPublicMedia
git pull
sudo systemctl restart plex-mounter
```

## 🛡️ Security Tasks

### 1. Change Password (CRITICAL!)

```bash
# On your server
cd /opt/findPublicMedia
nano users.json
```

Change `"password": "changeme"` to a strong password

```bash
sudo systemctl restart plex-mounter
```

### 2. Add More Users

Edit `users.json`:
```json
{
  "admin": {
    "password": "strong-password",
    "role": "admin"
  },
  "john": {
    "password": "another-strong-password",
    "role": "user"
  }
}
```

### 3. Set Up SSL (Recommended)

If you have a domain name:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📁 File Locations

| What | Where |
|------|-------|
| Application | `/opt/findPublicMedia/` |
| User database | `/opt/findPublicMedia/users.json` |
| Server config | `~/.plex_server_config.json` |
| Service file | `/etc/systemd/system/plex-mounter.service` |
| Nginx config | `/etc/nginx/sites-available/plex-mounter` |
| Logs | `journalctl -u plex-mounter` |

## 🌐 Access Options

### Option 1: Direct IP Access
- URL: `http://138.199.161.86:5001`
- Simple, works immediately
- Not encrypted (HTTP only)

### Option 2: With Nginx + SSL (Recommended)
- URL: `https://your-domain.com`
- Encrypted (HTTPS)
- Professional look
- Requires domain name

### Option 3: Cloudflare Tunnel (Free, No Port Forwarding)
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Create tunnel
cloudflared tunnel create plex-mounter
cloudflared tunnel route dns plex-mounter movies.yourdomain.com
cloudflared tunnel run --url http://localhost:5001 plex-mounter
```

## 🐛 Troubleshooting

### Service won't start
```bash
sudo journalctl -u plex-mounter -n 50 --no-pager
```

### Can't login
- Check `users.json` exists and has valid JSON
- Restart service: `sudo systemctl restart plex-mounter`

### Movies not mounting
- Check server config in web UI
- Test SSH: `ssh root@138.199.161.86`
- Check logs: `sudo journalctl -u plex-mounter -f`

### Port already in use
Edit `/etc/systemd/system/plex-mounter.service`:
```
Environment="PORT=5002"
```
Then: `sudo systemctl daemon-reload && sudo systemctl restart plex-mounter`

## 📊 Monitoring

### Check if it's running
```bash
curl http://localhost:5001/login
# Should return HTML
```

### Check WebSocket
Open browser console on dashboard:
```javascript
// Should see: "Socket connected successfully"
```

### Check disk space
```bash
df -h /home/root/PlexMovies
```

## 🔄 Updates

Pull latest version:
```bash
cd /opt/findPublicMedia
git pull
sudo systemctl restart plex-mounter
```

## 💡 Tips

- **Use Select All** for batch mounting
- **Monitor progress** in real-time via WebSocket
- **Configure server once** via UI, saves to config file
- **Check logs regularly** for errors
- **Backup users.json** before changes
- **Use strong passwords** for production

---

## 🆘 Quick Help

**Installation issue?** → Check [deployment/README.md](deployment/README.md)  
**Configuration issue?** → Check [DEPLOYMENT.md](DEPLOYMENT.md)  
**Using the app?** → Check [README.md](README.md)

---

**Version**: 2.2.0  
**Last Updated**: 2024  
**Repository**: https://github.com/romo9889/findPublicMedia
