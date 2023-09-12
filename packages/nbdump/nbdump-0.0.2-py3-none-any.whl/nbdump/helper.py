import sys
from pathlib import Path


def generate_target_files(paths: list[str]) -> list[Path]:
    """
    Given a list of path:
    * If element is a dir, recursively add subfiles
    * If element is a file, add as is
    * Ignore the rest

    Args:
        root (list[str]): List of paths entered by user

    Returns:
        list[Path]: list of file path, no directories
    """
    unique_paths = set()
    for path in paths:
        path = Path(path)
        if not path.exists():
            print(f"[WARN] {path} does not exist, skipped.", file=sys.stderr)
        elif path.is_dir():
            unique_paths |= set([p for p in path.rglob("*.*") if p.is_file()])
        elif path.is_file():
            unique_paths.add(path)
        else:
            print(f"[WARN] {path} is not supported, skipped.", file=sys.stderr)
    return sorted(unique_paths)


def dedup_folders(files: list[Path]) -> list[Path]:
    """Extract parent folders from given paths"""
    unique_folders = {file.parent for file in files}
    unique_folders.discard(Path("."))
    return sorted(unique_folders)


def construct_mkdir_commands(folders: list[Path]) -> str:
    """Make mkdir commands so that %%writefile does not fail"""
    return "\n".join([f'!mkdir -p "{folder}"' for folder in folders])
