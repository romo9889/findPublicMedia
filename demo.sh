#!/bin/bash
# Demo script showing all streaming features

echo "🎬 findPublicMedia Streaming Demo"
echo "=================================="
echo ""

echo "📋 Demo 1: Integrated Search + Stream"
echo "Search for 'His Girl Friday' and stream instantly in VLC"
echo ""
echo "Command: python3 vibe_streamer.py 'His Girl Friday' --stream"
echo ""
read -p "Press Enter to run (or Ctrl+C to skip)..."
python3 vibe_streamer.py "His Girl Friday" --stream
echo ""

echo "=================================="
echo ""
echo "📋 Demo 2: Direct Stream from Archive.org Link"
echo "Stream 'Night of the Living Dead' directly"
echo ""
echo "Command: python3 stream_now.py --ia-link 'https://archive.org/details/NightOfTheLivingDead-MPEG' --mode quick"
echo ""
read -p "Press Enter to run (or Ctrl+C to skip)..."
python3 stream_now.py --ia-link "https://archive.org/details/NightOfTheLivingDead-MPEG" --mode quick
echo ""

echo "=================================="
echo ""
echo "📋 Demo 3: Mount for Plex (dry run - shows instructions)"
echo "Set up rclone mount for Plex/Jellyfin"
echo ""
echo "Command: python3 stream_now.py --ia-link 'https://archive.org/details/Charade_201712' --mode plex"
echo ""
read -p "Press Enter to see mount instructions (or Ctrl+C to skip)..."
python3 stream_now.py --ia-link "https://archive.org/details/Charade_201712" --mode plex
echo ""

echo "=================================="
echo ""
echo "📋 Demo 4: Search with Subtitles"
echo "Find movie and OpenSubtitles link"
echo ""
echo "Command: python3 vibe_streamer.py 'Charade' --subs-lang en --no-open"
echo ""
read -p "Press Enter to run (or Ctrl+C to skip)..."
python3 vibe_streamer.py "Charade" --subs-lang en --no-open
echo ""

echo "=================================="
echo ""
echo "✅ Demo Complete!"
echo ""
echo "Try these commands yourself:"
echo ""
echo "  # Quick stream"
echo "  python3 vibe_streamer.py 'Movie Title' --stream"
echo ""
echo "  # Mount for Plex"
echo "  python3 vibe_streamer.py 'Movie Title' --plex"
echo ""
echo "  # Direct link"
echo "  python3 stream_now.py --ia-link 'https://archive.org/details/...' --mode quick"
echo ""
