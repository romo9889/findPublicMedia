#!/usr/bin/env python3
"""
Reorganize existing mounts into collection folders.
"""
from pathlib import Path
import subprocess
import sys

# Define collections
CLASSIC_GERMAN = [
    "DasKabinettdesDoktorCaligariTheCabinetofDrCaligari",
    "Nosferatu_most_complete_version_93_mins.",
    "TriumphOfTheWillgermanTriumphDesWillens",
]

FIRST_TRY = [
    "ANALOG_RECYCLING_VJ_LOOPS",
    "AsYouLikeIt1936",
    "CHILD",
    "Caligari_AnExquisiteCorpse",
    "DontBeaS1947",
    "Escape_From_Sobibor.avi",
    "Hitch_Hiker",
    "MakeMine1948",
    "ScarletStreet",
    "Shogun_Miniseries",
    "Televisi1960",
    "TheChase_",
    "TheNakedWitch",
    "TheStranger_0",
    "The_Absolute_Truth_About_Muhammad_in_the_Bible_With_Arabic_Subtitles",
    "his_girl_friday",
    "isforAto1953",
    "suddenly",
    "thekillers1946usafeaturingburtlancasteravagardneredmondobrienfilmnoirfullmovie_202001",
    "utopia",
]

MOUNT_BASE = Path.home() / "ArchiveMount"
ARCHIVE_DOWNLOAD_URL = "https://archive.org/download/"


def unmount_item(identifier: str):
    """Unmount a single item."""
    mount_path = MOUNT_BASE / identifier
    if not mount_path.exists():
        return False
    
    try:
        # Try umount (macOS/Linux)
        subprocess.run(["umount", str(mount_path)], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        try:
            # Try fusermount (Linux with FUSE)
            subprocess.run(["fusermount", "-u", str(mount_path)], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


def mount_item(identifier: str, collection_path: Path):
    """Mount item into collection folder."""
    # Create mount point
    mount_path = collection_path / identifier
    mount_path.mkdir(parents=True, exist_ok=True)
    
    # Extract base URL
    import urllib.parse
    base_url = f"{ARCHIVE_DOWNLOAD_URL}{urllib.parse.quote(identifier)}/"
    
    # Create rclone config
    config_name = f"archive_{identifier.replace('-', '_')[:50]}"
    config_content = f"""[{config_name}]
type = http
url = {base_url}
"""
    
    rclone_config_dir = Path.home() / ".config" / "rclone"
    rclone_config_dir.mkdir(parents=True, exist_ok=True)
    rclone_config_file = rclone_config_dir / "rclone.conf"
    
    # Check if config exists
    existing_config = ""
    if rclone_config_file.exists():
        existing_config = rclone_config_file.read_text()
    
    if f"[{config_name}]" not in existing_config:
        with open(rclone_config_file, "a") as f:
            f.write("\n" + config_content)
    
    # Mount command
    mount_cmd = [
        "rclone", "mount",
        f"{config_name}:", str(mount_path),
        "--read-only",
        "--vfs-cache-mode", "full",
        "--daemon"
    ]
    
    try:
        subprocess.run(mount_cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    print("🔄 Reorganizing mounts into collection folders...\n")
    
    # Create collection folders
    first_try_path = MOUNT_BASE / "first_try"
    classic_german_path = MOUNT_BASE / "classic_german"
    first_try_path.mkdir(parents=True, exist_ok=True)
    classic_german_path.mkdir(parents=True, exist_ok=True)
    
    # Process classic German films
    print("📂 Processing classic_german collection...")
    for identifier in CLASSIC_GERMAN:
        print(f"  🎬 {identifier}")
        if unmount_item(identifier):
            print(f"     ✓ Unmounted")
            if mount_item(identifier, classic_german_path):
                print(f"     ✓ Remounted to classic_german/{identifier}")
            else:
                print(f"     ✗ Failed to remount")
        else:
            print(f"     ⚠ Already unmounted or not found")
    
    # Process first try films
    print("\n📂 Processing first_try collection...")
    for identifier in FIRST_TRY:
        print(f"  🎬 {identifier}")
        if unmount_item(identifier):
            print(f"     ✓ Unmounted")
            if mount_item(identifier, first_try_path):
                print(f"     ✓ Remounted to first_try/{identifier}")
            else:
                print(f"     ✗ Failed to remount")
        else:
            print(f"     ⚠ Already unmounted or not found")
    
    print("\n✅ Reorganization complete!")
    print(f"\n📁 Collections:")
    print(f"   {first_try_path}")
    print(f"   {classic_german_path}")


if __name__ == "__main__":
    main()
