#!/usr/bin/env python3
"""
Server Setup for Plex Library (Multi-Project Server Compatible)

This script helps you set up Plex library hosting on a server that's
already running other projects (shop, n8n, etc.) without interference.

Security:
- Credentials are NEVER stored in git
- Config saved to ~/.plex_server_config.json (local only, gitignored)
- File permissions set to 600 (user read/write only)
"""

import os
import sys
import json
import subprocess
from pathlib import Path


CONFIG_PATH = os.path.expanduser("~/.plex_server_config.json")


def print_header():
    """Print welcome message."""
    print("\n" + "="*70)
    print("  🎬 Plex Library Server Setup (Multi-Project Server)")
    print("="*70)
    print("\n⚠️  SECURITY: All credentials stored locally only")
    print(f"   Config file: {CONFIG_PATH} (gitignored)")
    print("\n📌 This server can host multiple projects simultaneously:")
    print("   ✓ Shop (existing)")
    print("   ✓ n8n (planned)")  
    print("   ✓ Plex Movies (this setup)")
    print()


def get_server_config():
    """
    Interactive prompts to get server configuration.
    Asks for IP and credentials without storing passwords in git.
    """
    print_header()
    
    config = {}
    
    # Get server details
    print("📡 Server Connection Details:")
    print("-" * 40)
    config['host'] = input("Server IP address: ").strip()
    config['username'] = input("SSH Username: ").strip()
    config['port'] = input("SSH Port [22]: ").strip() or "22"
    
    # Suggest common paths for media storage
    print("\n📁 Where to store Plex movies on your server?")
    print("   Suggested paths:")
    print(f"   • /home/{config['username']}/PlexMovies (user directory)")
    print("   • /var/media/PlexMovies (common for web servers)")
    print("   • /opt/plex/movies (dedicated opt directory)")
    print("   • /mnt/storage/PlexMovies (mounted storage)")
    print()
    
    default_path = f"/home/{config['username']}/PlexMovies"
    remote_path = input(f"Remote path [{default_path}]: ").strip()
    config['remote_path'] = remote_path if remote_path else default_path
    
    # Check for SSH key
    print("\n🔐 Authentication Method:")
    print("-" * 40)
    ssh_key = os.path.expanduser("~/.ssh/id_rsa")
    ssh_key_pub = os.path.expanduser("~/.ssh/id_ed25519")
    
    if os.path.exists(ssh_key) or os.path.exists(ssh_key_pub):
        key_path = ssh_key if os.path.exists(ssh_key) else ssh_key_pub
        print(f"✓ Found SSH key: {key_path}")
        config['use_key'] = True
        print("  Using key-based authentication (recommended)")
    else:
        print("⚠️  No SSH key found")
        print("  You'll be prompted for password during copy")
        print("\n  To set up SSH key (recommended for security):")
        print(f"    ssh-copy-id -p {config['port']} {config['username']}@{config['host']}")
        print()
        use_password = input("Continue with password authentication? (y/n): ").strip().lower()
        if use_password != 'y':
            print("\nSetup cancelled. Please set up SSH key first.")
            sys.exit(0)
        config['use_key'] = False
    
    return config


def test_connection(config):
    """
    Test SSH connection and verify/create remote directory.
    """
    print("\n🔍 Testing Connection")
    print("=" * 70)
    
    # Test SSH connection
    print(f"\n1️⃣  Testing SSH connection to {config['host']}...")
    cmd = [
        'ssh',
        '-p', config['port'],
        '-o', 'ConnectTimeout=10',
        '-o', 'BatchMode=no',  # Allow interactive prompts
        f"{config['username']}@{config['host']}",
        'echo "✓ SSH connection successful"'
    ]
    
    try:
        # Run without capturing output so passphrase prompt works
        result = subprocess.run(cmd, timeout=30)
        if result.returncode == 0:
            print("✓ SSH connection successful")
        else:
            print(f"✗ SSH connection failed!")
            print("\n   Troubleshooting:")
            print(f"   • Can you SSH manually? Try: ssh -p {config['port']} {config['username']}@{config['host']}")
            print("   • Check if server is running and accessible")
            print("   • Verify firewall allows SSH connections")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Connection timeout (server not responding)")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Check/create remote directory
    print(f"\n2️⃣  Preparing directory: {config['remote_path']}...")
    check_cmd = [
        'ssh',
        '-p', config['port'],
        '-o', 'BatchMode=no',  # Allow interactive prompts
        f"{config['username']}@{config['host']}",
        f'mkdir -p "{config["remote_path"]}" && echo "✓ Directory ready"'
    ]
    
    try:
        # Run without capturing output so passphrase prompt works
        result = subprocess.run(check_cmd, timeout=30)
        if result.returncode == 0:
            print("✓ Directory ready")
            print(f"   Path: {config['username']}@{config['host']}:{config['remote_path']}")
            return True
        else:
            print(f"✗ Could not create directory!")
            print("\n   You may need to:")
            print(f"   • Create directory manually: mkdir -p {config['remote_path']}")
            print("   • Check write permissions")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def copy_to_server(config):
    """
    Copy Plex library to server using rsync.
    Follows symlinks to copy actual video files.
    """
    print("\n📦 Copying Plex Library to Server")
    print("=" * 70)
    
    local_path = os.path.expanduser("~/PlexMovies/")
    
    if not os.path.exists(local_path):
        print(f"\n✗ Local Plex library not found: {local_path}")
        print("\n   Please create the library first:")
        print("   python3 create_plex_library.py")
        return False
    
    # Count files
    try:
        file_count = 0
        dir_count = 0
        for root, dirs, files in os.walk(local_path):
            dir_count += len(dirs)
            file_count += len(files)
        print(f"\n📊 Found {file_count} files in {dir_count} directories")
    except Exception as e:
        print(f"   Warning: Could not count files: {e}")
    
    # Build rsync command
    # -L flag follows symlinks (copies actual files, not symlinks)
    cmd = [
        'rsync',
        '-avzL',  # archive, verbose, compress, follow symlinks
        '--progress',
        '--stats',
        '-e', f'ssh -p {config["port"]} -o BatchMode=no',  # Allow interactive passphrase
        local_path,
        f'{config["username"]}@{config["host"]}:{config["remote_path"]}/'
    ]
    
    print(f"\n📁 Source: {local_path}")
    print(f"📁 Destination: {config['username']}@{config['host']}:{config['remote_path']}/")
    print("\n⚠️  Important:")
    print("   • This copies actual video files (following symlinks)")
    print("   • Depending on file size and network speed, this may take a while")
    print("   • You can press Ctrl+C to cancel")
    print()
    
    proceed = input("Start copy? (y/n): ").strip().lower()
    if proceed != 'y':
        print("\n❌ Copy cancelled")
        return False
    
    print("\n🚀 Starting copy...")
    print("-" * 70)
    
    try:
        result = subprocess.run(cmd, text=True)
        if result.returncode == 0:
            print("\n" + "=" * 70)
            print("✅ Copy completed successfully!")
            print("=" * 70)
            return True
        else:
            print("\n✗ Copy failed (exit code: {result.returncode})")
            return False
    except KeyboardInterrupt:
        print("\n\n⚠️  Copy interrupted by user")
        print("   Files may be partially copied")
        return False
    except Exception as e:
        print(f"\n✗ Error during copy: {e}")
        return False


def save_config(config):
    """Save configuration to local file."""
    try:
        # Don't save passwords
        config_to_save = {k: v for k, v in config.items() if k != 'password'}
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config_to_save, f, indent=2)
        
        # Set secure permissions (user read/write only)
        os.chmod(CONFIG_PATH, 0o600)
        
        print(f"\n✓ Configuration saved to: {CONFIG_PATH}")
        print("  (File permissions: 600 - secure)")
        return True
    except Exception as e:
        print(f"\n⚠️  Warning: Could not save config: {e}")
        return False


def print_next_steps(config):
    """Print next steps for user."""
    print("\n" + "="*70)
    print("  ✅ Setup Complete!")
    print("="*70)
    
    print("\n📋 Next Steps:")
    print("-" * 70)
    
    print("\n1️⃣  Verify files on your server:")
    print(f"    ssh -p {config['port']} {config['username']}@{config['host']}")
    print(f"    ls -la {config['remote_path']}/PlexMovies/")
    print("    # You should see your organized movie folders")
    
    print("\n2️⃣  Configure Plex on your server:")
    print("    • Install Plex Media Server on your server")
    print(f"    • Add Movie library pointing to: {config['remote_path']}/PlexMovies/")
    print("    • Plex will scan and organize your movies")
    
    print("\n3️⃣  (Optional) Mount new movies directly to server:")
    print("    python3 update_mount_scripts.py")
    print("    ⚠️  Only after verifying files are on server!")
    
    print("\n📊 Your Server Now Hosts:")
    print("-" * 70)
    print("    ✓ Shop (your existing project)")
    print("    ✓ n8n (planned)")
    print(f"    ✓ Plex Movies → {config['remote_path']}/PlexMovies/")
    print("\n    All services run independently without conflicts! 🎉")
    print()


def main():
    """Main setup flow."""
    try:
        config = get_server_config()
        
        if not test_connection(config):
            print("\n❌ Setup failed: Could not connect to server")
            print("\n   Please check:")
            print("   • Server IP and port are correct")
            print("   • SSH service is running on server")
            print("   • Firewall allows SSH connections")
            print("   • Your credentials are correct")
            sys.exit(1)
        
        if not copy_to_server(config):
            print("\n❌ Setup failed: Could not copy files")
            sys.exit(1)
        
        save_config(config)
        print_next_steps(config)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
