#!/usr/bin/env python3
"""
Helper script to manage Archive.org rclone mounts for Plex/Jellyfin.

Usage:
  python mount_archive.py mount <identifier>    # Mount an Archive.org item
  python mount_archive.py unmount <identifier>  # Unmount a specific item
  python mount_archive.py list                  # List all active mounts
  python mount_archive.py unmount-all           # Unmount all Archive.org mounts
"""
import argparse
import subprocess
import sys
from pathlib import Path


def get_mount_dir(identifier: str = None) -> Path:
    """Get the mount directory path."""
    base = Path.home() / "ArchiveMount"
    if identifier:
        return base / identifier
    return base


def list_mounts():
    """List all active Archive.org mounts."""
    mount_base = get_mount_dir()
    if not mount_base.exists():
        print("No mounts found.")
        return
    
    mounts = []
    for item in mount_base.iterdir():
        if item.is_dir():
            # Check if actually mounted
            try:
                result = subprocess.run(
                    ["mount"],
                    capture_output=True,
                    text=True
                )
                if str(item) in result.stdout:
                    mounts.append(item.name)
            except:
                pass
    
    if mounts:
        print("Active Archive.org mounts:")
        for m in mounts:
            print(f"  - {m} → {get_mount_dir(m)}")
    else:
        print("No active mounts found.")


def unmount_item(identifier: str):
    """Unmount a specific Archive.org item."""
    mount_point = get_mount_dir(identifier)
    
    if not mount_point.exists():
        print(f"Mount point does not exist: {mount_point}")
        return
    
    print(f"Unmounting: {mount_point}")
    
    # Try fusermount first (Linux/macOS with FUSE)
    try:
        subprocess.run(["fusermount", "-u", str(mount_point)], check=True)
        print(f"✅ Unmounted: {identifier}")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Try umount (macOS/Linux)
    try:
        subprocess.run(["umount", str(mount_point)], check=True)
        print(f"✅ Unmounted: {identifier}")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Try rclone umount
    try:
        subprocess.run(["rclone", "umount", str(mount_point)], check=True)
        print(f"✅ Unmounted: {identifier}")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    print(f"❌ Failed to unmount. Try manually:")
    print(f"   fusermount -u {mount_point}")
    print(f"   or")
    print(f"   umount {mount_point}")


def unmount_all():
    """Unmount all Archive.org items."""
    mount_base = get_mount_dir()
    if not mount_base.exists():
        print("No mounts found.")
        return
    
    for item in mount_base.iterdir():
        if item.is_dir():
            unmount_item(item.name)


def mount_item(identifier: str):
    """Mount an Archive.org item (calls stream_now.py)."""
    print(f"To mount an item, use stream_now.py instead:")
    print(f"  python stream_now.py --ia-link https://archive.org/details/{identifier} --mode plex")


def main():
    parser = argparse.ArgumentParser(
        description="Manage Archive.org rclone mounts for Plex/Jellyfin."
    )
    parser.add_argument(
        "action",
        choices=["mount", "unmount", "list", "unmount-all"],
        help="Action to perform"
    )
    parser.add_argument(
        "identifier",
        nargs="?",
        help="Archive.org identifier (required for mount/unmount)"
    )
    
    args = parser.parse_args()
    
    if args.action == "list":
        list_mounts()
    elif args.action == "unmount-all":
        unmount_all()
    elif args.action == "mount":
        if not args.identifier:
            print("Error: identifier required for mount action")
            sys.exit(1)
        mount_item(args.identifier)
    elif args.action == "unmount":
        if not args.identifier:
            print("Error: identifier required for unmount action")
            sys.exit(1)
        unmount_item(args.identifier)


if __name__ == "__main__":
    main()
