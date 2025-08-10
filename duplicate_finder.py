#!/usr/bin/env python3
"""Utility to find and optionally delete duplicate files in a directory tree."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from collections import defaultdict
from typing import Dict, List


def file_hash(path: str, chunk_size: int = 8192) -> str:
    """Return the SHA-256 hash of the file at *path*."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(root: str) -> Dict[str, List[str]]:
    """Return mapping of hash -> list of paths for duplicate files under *root*."""
    hash_map: Dict[str, List[str]] = defaultdict(list)
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                digest = file_hash(path)
            except OSError as exc:  # e.g. permission error
                print(f"Unable to read {path}: {exc}", file=sys.stderr)
                continue
            hash_map[digest].append(path)
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def sort_paths_by_mtime(paths: List[str]) -> List[str]:
    """Return *paths* ordered by modification time, oldest first."""
    return sorted(paths, key=os.path.getmtime)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find duplicate files and optionally delete them.")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (defaults to current working directory)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete duplicate files, keeping one copy of each group",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without removing files",
    )
    args = parser.parse_args()

    duplicates = find_duplicates(args.directory)
    if not duplicates:
        print("No duplicates found.")
        return

    for paths in duplicates.values():
        ordered = sort_paths_by_mtime(paths)
        print("Duplicate group:")
        for p in ordered:
            print(f"  {p}")
        if args.delete:
            for p in ordered[1:]:  # keep oldest file
                if args.dry_run:
                    print(f"Would delete {p}")
                else:
                    os.remove(p)
                    print(f"Deleted {p}")


if __name__ == "__main__":
    main()
