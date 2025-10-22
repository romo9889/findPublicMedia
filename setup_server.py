#!/usr/bin/env python3
"""
Server configuration for Plex library.

This script helps you:
1. Set up your server connection
2. Copy PlexMovies to the server
3. Test the connection
4. Update mount scripts to use server location
"""
import os
import subprocess
from pathlib import Path
import json

CONFIG_FILE = Path.home() / ".plex_server_config.json"


def get_server_config():
    """Get or create server configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    
    print("\n" + "="*60)
    print("📡 SERVER CONFIGURATION")
    print("="*60)
    print("\nLet's set up your server connection.")
    print("\nCommon options:")
    print("1. Network share (SMB/AFP): e.g., /Volumes/ServerName/Movies")
    print("2. SSH/SFTP server: e.g., user@server:/path/to/movies")
    print("3. NAS: e.g., /Volumes/NAS/Media/Movies")
    print("4. External drive: e.g., /Volumes/MyDrive/PlexMovies")
    print()
    
    server_type = input("Server type (smb/ssh/nas/local): ").strip().lower()
    
    if server_type == "smb":
        print("\nSMB/Network Share Configuration:")
        server_address = input("  Server address (e.g., //192.168.1.100/Movies): ").strip()
        username = input("  Username (or press Enter if none): ").strip()
        mount_point = input("  Local mount point (e.g., /Volumes/ServerMovies): ").strip()
        
        config = {
            "type": "smb",
            "address": server_address,
            "username": username if username else None,
            "mount_point": mount_point,
            "plex_path": f"{mount_point}/PlexMovies"
        }
    
    elif server_type == "ssh":
        print("\nSSH/SFTP Configuration:")
        ssh_host = input("  SSH host (e.g., user@192.168.1.100): ").strip()
        remote_path = input("  Remote path (e.g., /mnt/media/PlexMovies): ").strip()
        
        config = {
            "type": "ssh",
            "host": ssh_host,
            "remote_path": remote_path,
            "plex_path": remote_path
        }
    
    elif server_type == "local":
        print("\nLocal/External Drive Configuration:")
        local_path = input("  Path (e.g., /Volumes/MyDrive/PlexMovies): ").strip()
        
        config = {
            "type": "local",
            "plex_path": local_path
        }
    
    else:  # nas or other
        print("\nNAS/Other Configuration:")
        path = input("  Full path to Plex library: ").strip()
        
        config = {
            "type": "nas",
            "plex_path": path
        }
    
    # Save config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {CONFIG_FILE}")
    return config


def test_connection(config):
    """Test server connection."""
    print("\n🔍 Testing connection...")
    
    server_type = config["type"]
    plex_path = config["plex_path"]
    
    if server_type == "local" or server_type == "nas":
        # Test local path
        path = Path(plex_path)
        if path.exists():
            print(f"✅ Path accessible: {plex_path}")
            return True
        else:
            print(f"❌ Path not accessible: {plex_path}")
            print("   Make sure the drive/share is mounted")
            return False
    
    elif server_type == "smb":
        # Test SMB mount
        mount_point = config["mount_point"]
        path = Path(mount_point)
        if path.exists():
            print(f"✅ SMB share mounted: {mount_point}")
            return True
        else:
            print(f"❌ SMB share not mounted: {mount_point}")
            print(f"   To mount: mount_smbfs {config['address']} {mount_point}")
            return False
    
    elif server_type == "ssh":
        # Test SSH connection
        try:
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=5", config["host"], "echo", "connected"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ SSH connection successful: {config['host']}")
                return True
            else:
                print(f"❌ SSH connection failed")
                return False
        except subprocess.TimeoutExpired:
            print(f"❌ SSH connection timeout")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return False


def copy_to_server(config):
    """Copy PlexMovies to server."""
    local_plex = Path.home() / "PlexMovies"
    server_plex = config["plex_path"]
    server_type = config["type"]
    
    print(f"\n📦 Copying PlexMovies to server...")
    print(f"   From: {local_plex}")
    print(f"   To:   {server_plex}")
    
    if not local_plex.exists():
        print("❌ Local PlexMovies directory not found!")
        return False
    
    try:
        if server_type == "ssh":
            # Use rsync over SSH
            cmd = [
                "rsync", "-avz", "--progress",
                f"{local_plex}/",
                f"{config['host']}:{server_plex}/"
            ]
            print(f"\nRunning: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        
        else:
            # Use rsync for local/SMB/NAS
            Path(server_plex).parent.mkdir(parents=True, exist_ok=True)
            cmd = [
                "rsync", "-av", "--progress",
                f"{local_plex}/",
                f"{server_plex}/"
            ]
            print(f"\nRunning: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        
        print("\n✅ Copy completed successfully!")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Copy failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("🎬 PLEX SERVER SETUP")
    print("="*60)
    
    # Get or create config
    config = get_server_config()
    
    print("\n" + "="*60)
    print("Current Configuration:")
    print("="*60)
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Test connection
    if not test_connection(config):
        print("\n⚠️  Connection test failed!")
        print("   Fix the connection and run this script again.")
        return 1
    
    # Ask to copy
    print("\n" + "="*60)
    response = input("\n🚀 Copy PlexMovies to server now? (y/n): ").strip().lower()
    
    if response == 'y':
        if copy_to_server(config):
            print("\n" + "="*60)
            print("✅ SETUP COMPLETE!")
            print("="*60)
            print(f"\n📁 Server Plex library: {config['plex_path']}")
            print("\n💡 Next steps:")
            print("   1. Verify files on server")
            print("   2. Point Plex server to the new location")
            print("   3. Run: python3 update_mount_scripts.py")
            print("      (This will update all mount scripts to use server)")
            return 0
        else:
            print("\n❌ Copy failed. Check errors above.")
            return 1
    else:
        print("\n⏭️  Skipped copy.")
        print("   Run this script again when ready to copy.")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
