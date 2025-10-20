#!/bin/bash
# Demo script for AI-powered mount list feature

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  🎬 AI-POWERED MOVIE MOUNT DEMO                              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "This demo will show you how to use natural language to find"
echo "and mount movies from Archive.org for Plex/Jellyfin."
echo ""
echo "Press ENTER to continue..."
read

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Example 1: Film Noir Collection"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Command:"
echo "  python3 ai_mount_list.py --prompt \"classic film noir from the 1940s\" --limit 5"
echo ""
echo "Press ENTER to run..."
read

python3 ai_mount_list.py --prompt "classic film noir from the 1940s" --limit 5 --yes

echo ""
echo "Press ENTER to continue to next example..."
read

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Example 2: Interactive Mode"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "You can also run interactively and type your own description:"
echo ""
echo "Command:"
echo "  python3 ai_mount_list.py"
echo ""
echo "Try it yourself! Describe what movies you want to watch:"
echo "(or press Ctrl+C to skip)"
echo ""

python3 ai_mount_list.py

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  ✨ DEMO COMPLETE!                                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Check your mounts: python3 mount_archive.py list"
echo "  2. Add ~/ArchiveMount to your Plex library"
echo "  3. Enjoy your movies!"
echo ""
