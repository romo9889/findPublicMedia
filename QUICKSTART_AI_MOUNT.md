# 🎬 Quick Reference: AI Mount List

## One-Liners

```bash
# Interactive mode
python3 ai_mount_list.py

# Quick mount with prompt
python3 ai_mount_list.py --prompt "your description here"

# Common examples
python3 ai_mount_list.py --prompt "film noir from the 1940s" --yes
python3 ai_mount_list.py --prompt "hitchcock thrillers" --limit 10
python3 ai_mount_list.py --prompt "sci-fi about AI" --yes
python3 ai_mount_list.py --prompt "silent comedies" --limit 5
```

## Management Commands

```bash
# List all mounts
python3 mount_archive.py list

# Unmount specific
python3 mount_archive.py unmount IDENTIFIER

# Unmount all
python3 mount_archive.py unmount-all
```

## Workflow

1. **Describe** what you want: `python3 ai_mount_list.py`
2. **Mount** happens automatically
3. **Scan** in Plex: Library → Scan Library Files
4. **Watch** your movies!

## Example Prompts

- "classic film noir from the 1940s"
- "sci-fi movies about artificial intelligence"  
- "hitchcock psychological thrillers"
- "silent comedies with charlie chaplin"
- "westerns with john wayne"
- "horror films from the 1930s"

## Tips

✅ Be specific but not too specific
✅ Use recognized film terms (noir, western, thriller)
✅ Combine era + genre for best results
✅ Try different phrasings if first attempt doesn't match

## Files Created

- `ai_mount_list.py` - Main script
- `mount_results.json` - Detailed results from last run
- `~/ArchiveMount/` - Mount directory for movies

## Full Documentation

- Complete guide: `AI_MOUNT_GUIDE.md`
- Plex setup: `PLEX_GUIDE.md`
- General usage: `README.md`
