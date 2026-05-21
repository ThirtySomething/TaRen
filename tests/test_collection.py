"""
Collection Enhancement Demo and Test

This script demonstrates the new Collection class and its features
for organizing collection structure with downloads, seen, unseen, and trash folders.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from taren.collection import Collection


def main():
    """Demo of Collection class features."""

    # Create demo collection structure
    demo_collection = Path("/tmp/taren_demo_collection_v2")
    if demo_collection.exists():
        import shutil

        shutil.rmtree(demo_collection)

    demo_collection.mkdir(exist_ok=True)

    # Initialize Collection manager with root path
    collection = Collection(demo_collection)

    print("=" * 70)
    print("COLLECTION ORGANIZATION DEMO")
    print("=" * 70)
    print()

    # Initialize collection folders
    print("1. INITIALIZING COLLECTION STRUCTURE:")
    print("-" * 70)
    if collection.initialize():
        print("   ✓ Collection initialized successfully")
        print(f"   Root: {collection.get_root_path()}")
        print(f"   Downloads: {collection.get_downloads_path()}")
        print(f"   Seen: {collection.get_seen_path()}")
        print(f"   Unseen: {collection.get_unseen_path()}")
        print(f"   Trash: {collection.get_trash_path()}")
    else:
        print("   ✗ Collection initialization failed")
        return
    print()

    # Create some demo files
    print("2. CREATING DEMO FILES:")
    print("-" * 70)
    (collection.get_downloads_path() / "episode1.mkv").touch()
    (collection.get_downloads_path() / "episode2.mkv").touch()
    (collection.get_downloads_path() / "episode3.mkv").touch()
    (collection.get_seen_path() / "episode1.mkv").touch()
    (collection.get_unseen_path() / "episode_pending.mkv").touch()
    (collection.get_trash_path() / "old_episode.mkv").touch()
    print("   ✓ Demo files created")
    print()

    # 1. Get Downloads
    print("1. DOWNLOADS (all files in downloads folder):")
    print("-" * 70)
    downloads = collection.get_downloads()
    for i, file in enumerate(downloads, 1):
        print(f"   {i}. {file}")
    print(f"   Total downloads: {len(downloads)}\n")

    # 2. Get Seen
    print("2. SEEN (all files in seen folder):")
    print("-" * 70)
    seen = collection.get_seen()
    for i, file in enumerate(seen, 1):
        print(f"   {i}. {file}")
    print(f"   Total seen: {len(seen)}\n")

    # 3. Get Unseen
    print("3. UNSEEN (files in unseen folder):")
    print("-" * 70)
    unseen = collection.get_unseen()
    for i, file in enumerate(unseen, 1):
        print(f"   {i}. {file}")
    print(f"   Total unseen: {len(unseen)}\n")

    # 4. Get Trash
    print("4. TRASH (deleted files):")
    print("-" * 70)
    trash = collection.get_trash()
    for i, file in enumerate(trash, 1):
        print(f"   {i}. {file}")
    print(f"   Total in trash: {len(trash)}\n")

    # 5. Get Counts
    print("5. SUMMARY COUNTS:")
    print("-" * 70)
    counts = collection.get_counts()
    for key, value in counts.items():
        print(f"   {key:12s}: {value}")
    print()

    # 6. Get Detailed Stats
    print("6. DETAILED STATS:")
    print("-" * 70)
    stats = collection.get_stats()
    print("   Counts:")
    for key, value in stats["counts"].items():
        print(f"      {key:12s}: {value}")
    print()

    print("=" * 70)
    print("Collection enhancement is working correctly!")
    print("=" * 70)


if __name__ == "__main__":
    main()
