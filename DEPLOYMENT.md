# Production Deployment Guide

## 🚀 Deploying to Production

This guide covers hosting the Public Media Mounter on a production server.

## Quick Deploy Options

### Option 1: Deploy on Same Server as Plex (Recommended)

Since you already have a server running Plex, deploy there:

```bash
# On your server (138.199.161.86)
cd /opt
git clone https://github.com/romo9889/findPublicMedia.git
cd findPublicMedia

# Install dependencies
python3 -m pip install -r requirements.txt

# Set production environment
export PRODUCTION=true
export SECRET_KEY="your-random-secret-key-here"
export PORT=5001

# Run with systemd (recommended)
sudo cp deployment/plex-mounter.service /etc/systemd/system/
sudo systemctl enable plex-mounter
sudo systemctl start plex-mounter
```

### Option 2: Deploy on Separate Server (Alternative)

If you want the web interface on a different server:

- Follow the same steps on your deployment server
- Configure SSH keys to connect to your Plex server
- Ensure network connectivity between servers

## 🔐 Security Setup

### 1. Change Default Password

**CRITICAL**: Change the default admin password immediately!

Edit `users.json` after first run:
```json
{
  "admin": {
    "password": "YOUR_STRONG_PASSWORD_HERE",
    "role": "admin"
  }
}
```

Or use password hashing (recommended):
```python
import hashlib
password = "your-password"
hashed = hashlib.sha256(password.encode()).hexdigest()
```

### 2. Set Secret Key

```bash
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
```

### 3. Configure Firewall

```bash
# Allow only specific IPs to access web interface
sudo ufw allow from YOUR_IP_ADDRESS to any port 5001

# Or use nginx reverse proxy with authentication
```

## 🌐 Nginx Reverse Proxy (Recommended)

### Install Nginx

```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

### Configure Nginx

Create `/etc/nginx/sites-available/plex-mounter`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_read_timeout 86400;
    }
}
```

Enable and get SSL:

```bash
sudo ln -s /etc/nginx/sites-available/plex-mounter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.com
```

## 📦 Systemd Service

Create `/etc/systemd/system/plex-mounter.service`:

```ini
[Unit]
Description=Public Media Mounter Web Interface
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/findPublicMedia
Environment="PRODUCTION=true"
Environment="SECRET_KEY=your-secret-key-here"
Environment="PORT=5001"
ExecStart=/usr/bin/python3 /opt/findPublicMedia/web_app_pro.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start and enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable plex-mounter
sudo systemctl start plex-mounter
sudo systemctl status plex-mounter
```

## 🔧 Environment Variables

```bash
# Production mode
export PRODUCTION=true

# Secret key for sessions (generate unique value!)
export SECRET_KEY="your-random-secret-key"

# Port to run on
export PORT=5001

# Optional: Custom config paths
export CONFIG_PATH="/etc/plex-mounter/config.json"
export USERS_PATH="/etc/plex-mounter/users.json"
```

## 👥 User Management

### Add New Users

Edit `users.json`:

```json
{
  "admin": {
    "password": "hashed-password",
    "role": "admin"
  },
  "john": {
    "password": "hashed-password",
    "role": "user"
  },
  "jane": {
    "password": "hashed-password",
    "role": "user"
  }
}
```

### Roles

- **admin**: Can configure server settings, manage users
- **user**: Can search and mount movies only

## 🐳 Docker Deployment (Alternative)

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PRODUCTION=true
ENV PORT=5001

EXPOSE 5001

CMD ["python3", "web_app_pro.py"]
```

Build and run:

```bash
docker build -t plex-mounter .
docker run -d \
  -p 5001:5001 \
  -v ~/.plex_server_config.json:/root/.plex_server_config.json \
  -v $(pwd)/users.json:/app/users.json \
  -e SECRET_KEY="your-secret-key" \
  --name plex-mounter \
  plex-mounter
```

## 📊 Monitoring

### View Logs

```bash
# Systemd logs
sudo journalctl -u plex-mounter -f

# Docker logs
docker logs -f plex-mounter
```

### Health Check

```bash
curl http://localhost:5001/login
```

## 🔄 Updates

```bash
cd /opt/findPublicMedia
git pull
sudo systemctl restart plex-mounter
```

## 🛡️ Security Checklist

- [ ] Changed default admin password
- [ ] Set unique SECRET_KEY
- [ ] Configured firewall (ufw/iptables)
- [ ] Set up SSL with Let's Encrypt
- [ ] Restricted access to specific IPs (optional)
- [ ] Enabled fail2ban for brute force protection
- [ ] Regular backups of users.json and config
- [ ] Monitor logs for suspicious activity

## 🌍 Access from Internet

### Port Forwarding

If hosting at home:

1. Forward port 5001 (or 80/443 if using nginx) on your router
2. Point to your server's local IP
3. Use dynamic DNS (DuckDNS, No-IP) for your changing public IP

### Cloudflare Tunnel (Recommended)

Free and secure alternative to port forwarding:

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Create tunnel
cloudflared tunnel create plex-mounter
cloudflared tunnel route dns plex-mounter your-subdomain.yourdomain.com
cloudflared tunnel run --url http://localhost:5001 plex-mounter
```

## 🔧 Troubleshooting

**WebSocket not working:**
- Ensure nginx config includes WebSocket headers
- Check firewall allows persistent connections

**Can't connect to Plex server:**
- Verify SSH keys are set up: `ssh root@138.199.161.86`
- Check server config in UI
- Test connection with: `curl http://localhost:5001/api/test-server`

**High CPU usage:**
- Limit concurrent mounts (modify code to queue)
- Increase server resources

## 📱 Mobile Access

The interface is fully responsive and works on phones/tablets. Just access your domain or IP from any device.

---

## Support

For issues, check logs first:
```bash
sudo journalctl -u plex-mounter -n 100 --no-pager
```
