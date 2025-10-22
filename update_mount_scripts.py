#!/usr/bin/env python3
"""
Update mount scripts to use server location for Plex library.

Run this AFTER setup_server.py has successfully copied your library.
"""
import json
from pathlib import Path
import re

CONFIG_FILE = Path.home() / ".plex_server_config.json"
SCRIPTS_TO_UPDATE = [
    "create_plex_library.py",
    "ai_mount_list.py",
    "stream_now.py"
]


def load_config():
    """Load server configuration."""
    if not CONFIG_FILE.exists():
        print(f"❌ Configuration not found: {CONFIG_FILE}")
        print("   Run setup_server.py first!")
        return None
    
    with open(CONFIG_FILE) as f:
        return json.load(f)


def update_create_plex_library(config):
    """Update create_plex_library.py to use server path."""
    file_path = Path("create_plex_library.py")
    
    if not file_path.exists():
        print(f"⚠️  Skipping {file_path.name} - not found")
        return False
    
    content = file_path.read_text()
    
    # Replace PLEX_LIBRARY = Path.home() / "PlexMovies"
    old_pattern = r'PLEX_LIBRARY = Path\.home\(\) / "PlexMovies"'
    new_line = f'PLEX_LIBRARY = Path("{config["plex_path"]}")'
    
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_line, content)
        file_path.write_text(content)
        print(f"✅ Updated {file_path.name}")
        return True
    else:
        print(f"⚠️  Pattern not found in {file_path.name}")
        return False


def update_ai_mount_list(config):
    """Update ai_mount_list.py - it uses create_plex_library.py so no changes needed."""
    print(f"ℹ️  ai_mount_list.py uses create_plex_library.py - no changes needed")
    return True


def update_stream_now(config):
    """Update stream_now.py - it uses create_plex_library.py so no changes needed."""
    print(f"ℹ️  stream_now.py uses create_plex_library.py - no changes needed")
    return True


def create_backup(filename):
    """Create backup of file before modifying."""
    file_path = Path(filename)
    if file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        backup_path.write_text(file_path.read_text())
        print(f"   📋 Backup created: {backup_path.name}")
        return True
    return False


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("🔧 UPDATE MOUNT SCRIPTS FOR SERVER")
    print("="*60)
    
    # Load config
    config = load_config()
    if not config:
        return 1
    
    print(f"\n📁 Server Plex path: {config['plex_path']}")
    print(f"   Type: {config['type']}\n")
    
    # Confirm
    response = input("Update all mount scripts to use server? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled.")
        return 0
    
    print("\n🔄 Updating scripts...\n")
    
    # Create backups
    for script in SCRIPTS_TO_UPDATE:
        if Path(script).exists():
            create_backup(script)
    
    # Update scripts
    success_count = 0
    
    if update_create_plex_library(config):
        success_count += 1
    
    update_ai_mount_list(config)
    update_stream_now(config)
    
    print("\n" + "="*60)
    print("✅ UPDATE COMPLETE!")
    print("="*60)
    print(f"\nUpdated {success_count} script(s)")
    print(f"\n📁 All future mounts will create Plex library at:")
    print(f"   {config['plex_path']}")
    print(f"\n💡 Test it:")
    print(f"   python3 create_plex_library.py")
    print(f"   (Should update files on server)")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
