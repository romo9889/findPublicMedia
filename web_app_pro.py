#!/usr/bin/env python3
"""
Public Media Mounter - Production Web Interface

Features:
- User authentication
- Real-time progress via WebSocket
- Movie preview and selection
- Server configuration UI
- Production-ready deployment
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import subprocess
import sys
import os
from pathlib import Path
import secrets
import threading
import time
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
socketio = SocketIO(app, cors_allowed_origins="*")

CONFIG_PATH = Path.home() / ".plex_server_config.json"
USERS_PATH = Path(__file__).parent / "users.json"

# Simple user store (use database in production)
def load_users():
    if USERS_PATH.exists():
        with open(USERS_PATH) as f:
            return json.load(f)
    # Default admin user (change password immediately!)
    default_users = {"admin": {"password": "changeme", "role": "admin"}}
    save_users(default_users)  # Create the file on first run
    return default_users

def save_users(users):
    with open(USERS_PATH, 'w') as f:
        json.dump(users, f, indent=2)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def check_server_config():
    """Check if server is configured."""
    if not CONFIG_PATH.exists():
        return None
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        required = ["host", "user", "port", "remote_path"]
        if all(k in config for k in required):
            return config
    except Exception:
        pass
    return None

def save_server_config(config):
    """Save server configuration."""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    os.chmod(CONFIG_PATH, 0o600)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        users = load_users()
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username].get('role', 'user')
            return jsonify({'success': True})
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if 'username' in session:
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Main page."""
    server_config = check_server_config()
    return render_template('dashboard.html', 
                         server_configured=server_config is not None,
                         server_info=server_config,
                         username=session.get('username'),
                         role=session.get('role'))

def normalize_title(title, identifier=""):
    """Normalize movie title for display."""
    import re
    # Remove Archive.org suffixes
    cleaned = re.sub(r'_\d{6}$', '', title)
    cleaned = re.sub(r'\s*\(.*?\)\s*$', '', cleaned)
    
    # If title is just the identifier, make it readable
    if identifier and cleaned.lower().replace('_', '').replace('-', '') == identifier.lower().replace('_', '').replace('-', ''):
        cleaned = identifier.replace('_', ' ').replace('-', ' ')
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
    
    # Remove special characters
    cleaned = re.sub(r'[<>:"/\\|?*\[\]]', '', cleaned)
    
    return cleaned.strip()

@app.route('/api/search-movies', methods=['POST'])
@login_required
def search_movies():
    """Search for movies without mounting - returns preview list."""
    data = request.json
    prompt = data.get('prompt', '').strip()
    limit = data.get('limit', 20)
    single_mode = data.get('single_mode', False)  # New: single movie mode
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    try:
        # Import search functions
        sys.path.insert(0, str(Path(__file__).parent))
        from ai_mount_list import search_movies_by_description, resolve_archive_identifiers
        from stream_now import fetch_metadata
        
        # For single mode, just search and return one result
        if single_mode:
            limit = 1
        
        # Search for movies
        movies = search_movies_by_description(prompt, limit)
        
        # Resolve Archive.org identifiers
        movies = resolve_archive_identifiers(movies)
        
        # Normalize titles and add metadata
        for movie in movies:
            if 'title' in movie:
                movie['original_title'] = movie['title']
                movie['title'] = normalize_title(movie['title'], movie.get('identifier', ''))
            
            # Try to fetch additional metadata from Archive.org
            if 'identifier' in movie:
                try:
                    metadata = fetch_metadata(movie['identifier'])
                    if metadata:
                        movie['year'] = metadata.get('year')
                        movie['description'] = metadata.get('description', '')[:200]
                        movie['duration'] = metadata.get('runtime')
                except:
                    pass
        
        # Return preview data
        return jsonify({
            'success': True,
            'movies': movies,
            'count': len(movies),
            'single_mode': single_mode
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mount-selected', methods=['POST'])
@login_required
def mount_selected():
    """Mount selected movies from preview."""
    data = request.json
    selected = data.get('selected', [])
    use_server = data.get('use_server', False)
    
    if not selected:
        return jsonify({'error': 'No movies selected'}), 400
    
    # Create a session ID for tracking
    session_id = secrets.token_hex(8)
    
    # Start mounting in background thread
    thread = threading.Thread(
        target=mount_movies_background,
        args=(selected, use_server, session_id)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': f'Starting to mount {len(selected)} movies...'
    })

def mount_movies_background(movies, use_server, session_id):
    """Mount movies in background and emit progress via WebSocket."""
    total = len(movies)
    
    for idx, movie in enumerate(movies, 1):
        identifier = movie.get('identifier')
        title = movie.get('title', identifier)
        year = movie.get('year')
        
        # Emit progress
        socketio.emit('mount_progress', {
            'session_id': session_id,
            'current': idx,
            'total': total,
            'title': title,
            'status': 'mounting'
        })
        
        try:
            # Mount the movie
            if use_server:
                cmd = [
                    sys.executable,
                    str(Path(__file__).parent / 'server_mount_plex.py'),
                    '--identifier', identifier,
                    '--title', title
                ]
                if year:
                    cmd.extend(['--year', str(year)])
            else:
                ia_link = f"https://archive.org/details/{identifier}"
                cmd = [
                    sys.executable,
                    str(Path(__file__).parent / 'stream_now.py'),
                    '--ia-link', ia_link,
                    '--mode', 'plex'
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                status = 'success'
            else:
                status = 'failed'
                
        except Exception as e:
            status = 'failed'
        
        # Emit completion
        socketio.emit('mount_progress', {
            'session_id': session_id,
            'current': idx,
            'total': total,
            'title': title,
            'status': status
        })
        
        time.sleep(1)  # Small delay between mounts
    
    # Emit final completion
    socketio.emit('mount_complete', {
        'session_id': session_id,
        'total': total
    })

@app.route('/api/server-config', methods=['GET', 'POST'])
@login_required
def server_config():
    """Get or update server configuration."""
    if request.method == 'GET':
        config = check_server_config()
        if config:
            return jsonify({
                'configured': True,
                'host': config.get('host'),
                'user': config.get('user'),
                'port': config.get('port'),
                'path': config.get('remote_path')
            })
        else:
            return jsonify({'configured': False})
    
    # POST - update configuration
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    config = {
        'host': data.get('host'),
        'user': data.get('user'),
        'port': int(data.get('port', 22)),
        'remote_path': data.get('remote_path')
    }
    
    # Validate required fields
    if not all([config['host'], config['user'], config['remote_path']]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    save_server_config(config)
    
    return jsonify({'success': True, 'message': 'Server configuration saved'})

@app.route('/api/test-server', methods=['POST'])
@login_required
def test_server():
    """Test SSH connection to server."""
    config = check_server_config()
    if not config:
        return jsonify({'error': 'No server configured'}), 400
    
    try:
        cmd = [
            'ssh', '-p', str(config['port']),
            '-o', 'ConnectTimeout=10',
            '-o', 'BatchMode=yes',
            f"{config['user']}@{config['host']}",
            'echo "OK"'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Connection successful'})
        else:
            return jsonify({'error': 'Connection failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check if production mode
    production = os.environ.get('PRODUCTION', '').lower() in ['true', '1', 'yes']
    
    if not production:
        print("\n" + "="*60)
        print("🎬  PUBLIC MEDIA MOUNTER - PRODUCTION WEB INTERFACE")
        print("="*60)
        print("\n⚠️  DEVELOPMENT MODE")
        print("📍 Default credentials: admin / changeme")
        print("🔒 Change password immediately in production!")
        print("\n🌐 Starting web server...")
        print("📍 Open your browser to: http://localhost:5001")
        print("\n💡 Press Ctrl+C to stop the server\n")
    
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, 
                debug=not production,
                host='0.0.0.0' if production else '127.0.0.1',
                port=int(os.environ.get('PORT', 5001)),
                allow_unsafe_werkzeug=True)  # Allow Werkzeug in production for simplicity
