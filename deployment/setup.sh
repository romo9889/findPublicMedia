#!/bin/bash

# Quick Setup Script for Production Deployment
# Run this on your production server

set -e

echo "🚀 Public Media Mounter - Production Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run as root or with sudo"
    exit 1
fi

# Install directory
INSTALL_DIR="/opt/findPublicMedia"

echo "📦 Installing dependencies..."
apt update
apt install -y python3 python3-pip git nginx certbot python3-certbot-nginx

echo ""
echo "📥 Cloning repository..."
if [ -d "$INSTALL_DIR" ]; then
    echo "Directory $INSTALL_DIR already exists. Pulling latest changes..."
    cd "$INSTALL_DIR"
    git pull
else
    git clone https://github.com/romo9889/findPublicMedia.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "🐍 Installing Python packages..."
python3 -m pip install -r requirements.txt

echo ""
echo "🔑 Generating secret key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

echo ""
echo "📝 Setting up systemd service..."
cp deployment/plex-mounter.service /etc/systemd/system/
sed -i "s|CHANGE_THIS_TO_A_RANDOM_SECRET_KEY|$SECRET_KEY|g" /etc/systemd/system/plex-mounter.service

echo ""
echo "🌐 Do you want to set up Nginx reverse proxy? (y/n)"
read -r SETUP_NGINX

if [ "$SETUP_NGINX" = "y" ]; then
    echo "Enter your domain name (e.g., movies.yourdomain.com):"
    read -r DOMAIN
    
    cp deployment/nginx.conf /etc/nginx/sites-available/plex-mounter
    sed -i "s|your-domain.com|$DOMAIN|g" /etc/nginx/sites-available/plex-mounter
    
    ln -sf /etc/nginx/sites-available/plex-mounter /etc/nginx/sites-enabled/
    nginx -t
    systemctl reload nginx
    
    echo ""
    echo "🔒 Setting up SSL with Let's Encrypt..."
    certbot --nginx -d "$DOMAIN"
else
    echo "Skipping Nginx setup. Service will be available on http://YOUR_IP:5001"
fi

echo ""
echo "🔄 Starting service..."
systemctl daemon-reload
systemctl enable plex-mounter
systemctl start plex-mounter

echo ""
echo "✅ Installation complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 IMPORTANT NEXT STEPS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 🔐 CHANGE DEFAULT PASSWORD"
echo "   Edit: $INSTALL_DIR/users.json"
echo "   Default: admin / changeme"
echo ""
echo "2. 🔧 Configure Plex Server"
echo "   Visit the web interface and click 'Configure Server'"
echo "   Or edit: ~/.plex_server_config.json"
echo ""
echo "3. 📊 Check service status:"
echo "   systemctl status plex-mounter"
echo ""
echo "4. 📝 View logs:"
echo "   journalctl -u plex-mounter -f"
echo ""

if [ "$SETUP_NGINX" = "y" ]; then
    echo "5. 🌐 Access at: https://$DOMAIN"
else
    echo "5. 🌐 Access at: http://$(hostname -I | awk '{print $1}'):5001"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
