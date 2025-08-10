#!/usr/bin/env python3
"""Interactive GUI for inspecting and deleting duplicate files."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import Dict, List

from duplicate_finder import find_duplicates, sort_paths_by_mtime

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception as exc:  # pragma: no cover - ImportError when Tk not installed
    raise SystemExit(f"tkinter is required for the GUI: {exc}")


def _open_file(path: str) -> None:
    """Open *path* with the platform's default application."""
    try:
        if sys.platform.startswith("darwin"):
            subprocess.Popen(["open", path])
        elif os.name == "nt":  # type: ignore[attr-defined]
            os.startfile(path)  # pragma: no cover - Windows only
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as exc:
        messagebox.showerror("Error", f"Cannot open {path}: {exc}")


def _delete_file(path: str, frame: tk.Widget) -> None:
    """Remove *path* from disk and from the GUI."""
    if not messagebox.askyesno("Delete", f"Delete {path}?"):
        return
    try:
        os.remove(path)
        frame.destroy()
    except Exception as exc:
        messagebox.showerror("Error", f"Cannot delete {path}: {exc}")


def _build_ui(duplicates: Dict[str, List[str]]) -> None:
    root = tk.Tk()
    root.title("Duplicate Files")
    for paths in duplicates.values():
        ordered = sort_paths_by_mtime(paths)
        tk.Label(root, text=os.path.basename(ordered[0]), font=("Arial", 10, "bold")).pack(anchor="w")
        for p in ordered:
            row = tk.Frame(root)
            row.pack(anchor="w", padx=20)
            tk.Label(row, text=p).pack(side=tk.LEFT)
            tk.Button(row, text="View", command=lambda p=p: _open_file(p)).pack(side=tk.LEFT)
            tk.Button(row, text="Delete", command=lambda p=p, r=row: _delete_file(p, r)).pack(side=tk.LEFT)
    root.mainloop()


def main(directory: str = ".") -> None:
    """Launch the duplicate inspection GUI for *directory*."""
    duplicates = find_duplicates(directory)
    if not duplicates:
        print("No duplicates found.")
        return
    _build_ui(duplicates)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    main(target)
