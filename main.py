#!/usr/bin/env python3
"""
Public Media Mounter - Main Entry Point

Unified interface to mount Archive.org movies either:
- As a collection (batch mount from AI search)
- As a single movie (direct mount)

Supports both server (remote Plex) and local mounting with proper Plex structure.
"""
import json
import subprocess
import sys
from pathlib import Path


def check_server_config() -> dict | None:
    """Check if server is configured. Returns config dict or None."""
    config_path = Path.home() / ".plex_server_config.json"
    if not config_path.exists():
        return None
    try:
        with open(config_path) as f:
            config = json.load(f)
        # Validate required fields
        required = ["host", "user", "port", "remote_path"]
        if all(k in config for k in required):
            return config
    except Exception:
        pass
    return None


def setup_server():
    """Run server setup script."""
    print("\n🔧 Running server setup...\n")
    try:
        subprocess.run([sys.executable, "setup_server.py"], check=True)
        return check_server_config()
    except subprocess.CalledProcessError:
        print("❌ Server setup failed")
        return None


def mount_collection(use_server: bool):
    """Mount a collection of movies using AI search."""
    print("\n" + "="*60)
    print("📚 MOUNT COLLECTION (AI-Powered Search)")
    print("="*60)
    print("\nDescribe the movies you want to mount:")
    print("Examples:")
    print("  - 'classic film noir from the 1940s'")
    print("  - 'sci-fi movies about AI'")
    print("  - 'hitchcock thrillers'\n")
    
    prompt = input("Your description: ").strip()
    if not prompt:
        print("❌ No prompt provided")
        return
    
    limit = input("\nHow many movies (default 20): ").strip()
    if not limit:
        limit = "20"
    
    # Build command
    cmd = [sys.executable, "ai_mount_list.py", "--prompt", prompt, "--limit", limit]
    if use_server:
        cmd.append("--server")
    
    print(f"\n🚀 Searching and mounting{' on server' if use_server else ' locally'}...\n")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("❌ Collection mount failed")
    except KeyboardInterrupt:
        print("\n⏸️  Cancelled by user")


def mount_single_movie(use_server: bool):
    """Mount a single movie."""
    print("\n" + "="*60)
    print("🎬 MOUNT SINGLE MOVIE")
    print("="*60)
    print("\nEnter Archive.org link or identifier:")
    print("Examples:")
    print("  - https://archive.org/details/HisGirlFriday1940")
    print("  - HisGirlFriday1940\n")
    
    ia_input = input("Archive.org link/ID: ").strip()
    if not ia_input:
        print("❌ No input provided")
        return
    
    # If it's a full URL, use stream_now.py with server mode
    if ia_input.startswith("http"):
        if use_server:
            mode = "server"
        else:
            mode = "plex"
        
        cmd = [sys.executable, "stream_now.py", "--ia-link", ia_input, "--mode", mode]
    else:
        # Direct identifier - use server_mount_plex.py
        if use_server:
            print("\n📋 Optional: Provide title and year for better Plex organization")
            title = input("Title (or press Enter to skip): ").strip()
            year = input("Year (or press Enter to skip): ").strip()
            
            cmd = [sys.executable, "server_mount_plex.py", "--identifier", ia_input]
            if title:
                cmd.extend(["--title", title])
            if year:
                cmd.extend(["--year", year])
        else:
            # Local mount via stream_now
            ia_link = f"https://archive.org/details/{ia_input}"
            cmd = [sys.executable, "stream_now.py", "--ia-link", ia_link, "--mode", "plex"]
    
    print(f"\n🚀 Mounting{' on server' if use_server else ' locally'}...\n")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("❌ Mount failed")
    except KeyboardInterrupt:
        print("\n⏸️  Cancelled by user")


def choose_mount_location(server_config: dict | None) -> str:
    """Ask user where to mount. Returns 'server', 'local', or 'setup'."""
    if server_config:
        print(f"\n✅ Server configured: {server_config['user']}@{server_config['host']}")
        print("\nWhere do you want to mount?")
        print("  1. Server (remote Plex)")
        print("  2. Local (this computer)")
        choice = input("\nChoice (1/2): ").strip()
        return "server" if choice == "1" else "local"
    else:
        print("\n⚠️  No server configured yet")
        print("\nOptions:")
        print("  1. Set up server now")
        print("  2. Mount locally (this computer)")
        choice = input("\nChoice (1/2): ").strip()
        return "setup" if choice == "1" else "local"


def main_menu():
    """Display main menu and route to appropriate action."""
    print("\n" + "="*60)
    print("🎬  PUBLIC MEDIA MOUNTER  🎬")
    print("="*60)
    print("\nWhat do you want to mount?")
    print("  1. Mount a collection (AI search)")
    print("  2. Mount a single movie")
    print("  3. Exit")
    
    choice = input("\nChoice (1/2/3): ").strip()
    
    if choice == "3":
        print("\n👋 Goodbye!")
        return False
    
    if choice not in ["1", "2"]:
        print("❌ Invalid choice")
        return True
    
    # Check server config
    server_config = check_server_config()
    
    # Ask where to mount
    location = choose_mount_location(server_config)
    
    if location == "setup":
        server_config = setup_server()
        if not server_config:
            print("\n⚠️  Continuing with local mount")
            location = "local"
        else:
            location = "server"
    
    use_server = (location == "server")
    
    # Route to appropriate function
    if choice == "1":
        mount_collection(use_server)
    elif choice == "2":
        mount_single_movie(use_server)
    
    return True


def main():
    """Entry point."""
    try:
        while True:
            if not main_menu():
                break
            
            # Ask if user wants to continue
            print("\n" + "-"*60)
            continue_choice = input("\nMount something else? (y/n): ").strip().lower()
            if continue_choice not in ["y", "yes"]:
                print("\n👋 Goodbye!")
                break
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
