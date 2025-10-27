#!/usr/bin/env python3
"""
Public Media Mounter - Web Interface

A simple Flask web app for mounting Archive.org movies via a browser.
"""
from flask import Flask, render_template, request, jsonify, session
import json
import subprocess
import sys
import os
from pathlib import Path
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CONFIG_PATH = Path.home() / ".plex_server_config.json"


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


@app.route('/')
def index():
    """Main page."""
    server_config = check_server_config()
    return render_template('index.html', 
                         server_configured=server_config is not None,
                         server_info=server_config)


@app.route('/api/mount-collection', methods=['POST'])
def mount_collection():
    """Mount a collection via AI search."""
    data = request.json
    prompt = data.get('prompt', '').strip()
    limit = data.get('limit', 20)
    use_server = data.get('use_server', False)
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    # Build command
    cmd = [
        sys.executable,
        str(Path(__file__).parent / 'ai_mount_list.py'),
        '--prompt', prompt,
        '--limit', str(limit),
        '--yes'  # Skip confirmation
    ]
    
    if use_server:
        cmd.append('--server')
    
    try:
        # Run in background and return immediately
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit and check if it started successfully
        import time
        time.sleep(2)
        
        if process.poll() is None or process.returncode == 0:
            return jsonify({
                'status': 'started',
                'message': f'Searching for "{prompt}"... This may take a minute.',
                'location': 'server' if use_server else 'local'
            })
        else:
            stderr = process.stderr.read() if process.stderr else ''
            return jsonify({
                'error': f'Failed to start: {stderr}'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mount-single', methods=['POST'])
def mount_single():
    """Mount a single movie."""
    data = request.json
    ia_input = data.get('identifier', '').strip()
    title = data.get('title', '').strip()
    year = data.get('year', '').strip()
    use_server = data.get('use_server', False)
    
    if not ia_input:
        return jsonify({'error': 'No identifier provided'}), 400
    
    try:
        # If it's a full URL, use stream_now.py
        if ia_input.startswith('http'):
            mode = 'server' if use_server else 'plex'
            cmd = [
                sys.executable,
                str(Path(__file__).parent / 'stream_now.py'),
                '--ia-link', ia_input,
                '--mode', mode
            ]
        else:
            # Direct identifier
            if use_server:
                cmd = [
                    sys.executable,
                    str(Path(__file__).parent / 'server_mount_plex.py'),
                    '--identifier', ia_input
                ]
                if title:
                    cmd.extend(['--title', title])
                if year:
                    cmd.extend(['--year', year])
            else:
                # Local mount via stream_now
                ia_link = f"https://archive.org/details/{ia_input}"
                cmd = [
                    sys.executable,
                    str(Path(__file__).parent / 'stream_now.py'),
                    '--ia-link', ia_link,
                    '--mode', 'plex'
                ]
        
        # Run the command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit
        import time
        time.sleep(2)
        
        if process.poll() is None or process.returncode == 0:
            return jsonify({
                'status': 'started',
                'message': f'Mounting "{title or ia_input}"...',
                'location': 'server' if use_server else 'local'
            })
        else:
            stderr = process.stderr.read() if process.stderr else ''
            return jsonify({
                'error': f'Failed to mount: {stderr}'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/server-status')
def server_status():
    """Get server configuration status."""
    config = check_server_config()
    if config:
        return jsonify({
            'configured': True,
            'host': config.get('host'),
            'user': config.get('user'),
            'path': config.get('remote_path')
        })
    else:
        return jsonify({'configured': False})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬  PUBLIC MEDIA MOUNTER - WEB INTERFACE")
    print("="*60)
    print("\n🌐 Starting web server...")
    print("📍 Open your browser to: http://localhost:5001")
    print("\n💡 Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
