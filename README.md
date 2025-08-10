# TestProjects

This repository contains sample projects and utility scripts.

## duplicate_finder.py

`duplicate_finder.py` scans a directory tree for duplicate files and can optionally remove them, keeping the oldest copy of each duplicate group.

`duplicate_finder_gui.py` provides an interactive interface to inspect duplicates and delete individual copies.

### Usage

```
python duplicate_finder.py path/to/directory
python duplicate_finder.py path/to/directory --delete
python duplicate_finder.py path/to/directory --delete --dry-run

# Launch the interactive GUI
python duplicate_finder_gui.py path/to/directory
```

### Testing

Run the test suite with `pytest`:

```
pytest
```

