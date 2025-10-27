# Deployment Files

This directory contains everything needed for production deployment.

## Files

- **setup.sh** - Automated setup script for Ubuntu/Debian servers
- **plex-mounter.service** - Systemd service configuration
- **nginx.conf** - Nginx reverse proxy configuration with SSL

## Quick Start

### Option 1: Automated Setup (Recommended)

On your production server:

```bash
wget https://raw.githubusercontent.com/romo9889/findPublicMedia/main/deployment/setup.sh
chmod +x setup.sh
sudo ./setup.sh
```

### Option 2: Manual Setup

1. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git
   ```

2. **Clone repository**
   ```bash
   cd /opt
   sudo git clone https://github.com/romo9889/findPublicMedia.git
   cd findPublicMedia
   ```

3. **Install Python packages**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. **Set up systemd service**
   ```bash
   sudo cp deployment/plex-mounter.service /etc/systemd/system/
   # Edit the service file to set SECRET_KEY
   sudo nano /etc/systemd/system/plex-mounter.service
   sudo systemctl enable plex-mounter
   sudo systemctl start plex-mounter
   ```

5. **Optional: Set up Nginx**
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   sudo cp deployment/nginx.conf /etc/nginx/sites-available/plex-mounter
   # Edit the config file to set your domain
   sudo nano /etc/nginx/sites-available/plex-mounter
   sudo ln -s /etc/nginx/sites-available/plex-mounter /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Configuration

### Environment Variables

Edit `/etc/systemd/system/plex-mounter.service`:

- `PRODUCTION=true` - Enable production mode
- `SECRET_KEY` - **REQUIRED**: Generate with `python3 -c "import secrets; print(secrets.token_hex(32))"`
- `PORT=5001` - Port to run on

### User Management

Edit `/opt/findPublicMedia/users.json`:

```json
{
  "admin": {
    "password": "your-strong-password",
    "role": "admin"
  }
}
```

**⚠️ CRITICAL**: Change the default password immediately after deployment!

### Server Configuration

Configure via web UI or edit `~/.plex_server_config.json`:

```json
{
  "host": "138.199.161.86",
  "user": "root",
  "remote_path": "/home/root/PlexMovies"
}
```

## Monitoring

```bash
# Check service status
sudo systemctl status plex-mounter

# View logs
sudo journalctl -u plex-mounter -f

# Restart service
sudo systemctl restart plex-mounter
```

## Security Checklist

- [ ] Changed default admin password
- [ ] Set unique SECRET_KEY in systemd service
- [ ] Configured firewall
- [ ] Set up SSL with Let's Encrypt
- [ ] Restricted access (optional)

## Troubleshooting

**Service won't start:**
```bash
sudo journalctl -u plex-mounter -n 50
```

**Can't access web interface:**
- Check if service is running: `systemctl status plex-mounter`
- Check firewall: `sudo ufw status`
- Check port: `sudo netstat -tlnp | grep 5001`

**WebSocket issues:**
- Ensure Nginx config includes WebSocket headers
- Check browser console for errors

## Support

See [DEPLOYMENT.md](../DEPLOYMENT.md) for detailed documentation.
