import os
import subprocess
import sys
from pathlib import Path

# Ensure the project root is on the import path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from duplicate_finder import find_duplicates, file_hash, sort_paths_by_mtime


def create_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_file_hash(tmp_path):
    file = tmp_path / "data.txt"
    content = "hello world"
    create_file(file, content)
    assert file_hash(str(file)) == __import__("hashlib").sha256(content.encode()).hexdigest()


def test_find_duplicates(tmp_path):
    dir1 = tmp_path / "a.txt"
    dir2 = tmp_path / "sub" / "a_copy.txt"
    create_file(dir1, "same")
    create_file(dir2, "same")
    duplicates = find_duplicates(str(tmp_path))
    # Expect one group of duplicates with both file paths
    assert len(duplicates) == 1
    paths = next(iter(duplicates.values()))
    assert set(map(os.path.normpath, paths)) == {os.path.normpath(str(dir1)), os.path.normpath(str(dir2))}


def run_script(args):
    return subprocess.run([sys.executable, str(os.path.abspath("duplicate_finder.py"))] + args, check=True)


def test_delete_duplicates_dry_run(tmp_path):
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"
    create_file(file1, "same")
    create_file(file2, "same")
    run_script([str(tmp_path), "--delete", "--dry-run"])
    assert file1.exists() and file2.exists()


def test_delete_duplicates_keeps_oldest(tmp_path):
    older = tmp_path / "a.txt"
    newer = tmp_path / "b.txt"
    create_file(older, "same")
    create_file(newer, "same")
    os.utime(older, (0, 0))
    os.utime(newer, (1, 1))
    run_script([str(tmp_path), "--delete"])
    assert older.exists() and not newer.exists()


def test_sort_paths_by_mtime(tmp_path):
    older = tmp_path / "old.txt"
    newer = tmp_path / "new.txt"
    create_file(older, "a")
    create_file(newer, "b")
    os.utime(older, (0, 0))
    os.utime(newer, (1, 1))
    paths = [str(newer), str(older)]
    assert sort_paths_by_mtime(paths) == [str(older), str(newer)]
