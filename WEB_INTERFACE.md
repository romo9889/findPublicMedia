# Web Interface Guide

## 🌐 Starting the Web Interface

1. **Install dependencies** (first time only):
   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. **Start the server**:
   ```bash
   python3 web_app.py
   ```

3. **Open in browser**:
   Navigate to: http://localhost:5000

4. **Stop the server**:
   Press `Ctrl+C` in the terminal

## ✨ Features

### Mount a Collection
- Enter a natural language description
- Choose how many movies (1-50)
- Select server or local mounting
- Click "Search & Mount Collection"

**Example prompts:**
- "classic film noir from the 1940s"
- "sci-fi movies about artificial intelligence"
- "hitchcock psychological thrillers"

### Mount a Single Movie
- Enter Archive.org link or identifier
- Optionally add title and year for better naming
- Select server or local mounting
- Click "Mount Movie"

**Examples:**
- Link: `https://archive.org/details/HisGirlFriday1940`
- Identifier: `HisGirlFriday1940`

## 🎨 Interface

The web interface provides:
- ✅ Clean, modern design
- ✅ Server status indicator
- ✅ Real-time feedback
- ✅ Example prompts and IDs
- ✅ Mobile-responsive layout

## 🔒 Security Notes

- The web server runs on **localhost only** by default (127.0.0.1)
- For remote access, edit `web_app.py` and change `host='0.0.0.0'` (not recommended without authentication)
- Server credentials are read from `~/.plex_server_config.json` (never exposed to browser)

## 🛠️ Troubleshooting

**"Flask not found"**
```bash
python3 -m pip install Flask
```

**Port 5000 already in use**
Edit `web_app.py` and change `port=5000` to another port like `5001`

**Server configuration not showing**
Run the setup first:
```bash
python3 setup_server.py
```

## 📱 Access from Other Devices

To access from phones/tablets on your local network:

1. Find your computer's local IP (e.g., `192.168.1.100`)
2. Edit `web_app.py` line: `app.run(debug=True, host='0.0.0.0', port=5000)`
3. Restart the server
4. Access from other device: `http://192.168.1.100:5000`

⚠️ **Warning**: This exposes the interface to your local network. Only use on trusted networks.
