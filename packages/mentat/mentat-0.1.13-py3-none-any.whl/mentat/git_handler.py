import logging
import os
import subprocess
from pathlib import Path

from mentat.errors import UserError


def get_git_diff_for_path(git_root: Path, path: Path) -> str:
    return subprocess.check_output(["git", "diff", path], cwd=git_root).decode("utf-8")


def get_non_gitignored_files(path: Path) -> set[Path]:
    return set(
        # git returns / separated paths even on windows, convert so we can remove
        # glob_excluded_files, which have windows paths on windows
        Path(os.path.normpath(p))
        for p in filter(
            lambda p: p != "",
            subprocess.check_output(
                # -c shows cached (regular) files, -o shows other (untracked/new) files
                ["git", "ls-files", "-c", "-o", "--exclude-standard"],
                cwd=path,
                text=True,
            ).split("\n"),
        )
    )


def get_paths_with_git_diffs(git_root: Path) -> set[Path]:
    changed = subprocess.check_output(
        ["git", "diff", "--name-only"], cwd=git_root, text=True
    ).split("\n")
    new = subprocess.check_output(
        ["git", "ls-files", "-o", "--exclude-standard"], cwd=git_root, text=True
    ).split("\n")
    return set(
        map(
            lambda path: Path(os.path.realpath(os.path.join(git_root, Path(path)))),
            changed + new,
        )
    )


def _get_git_root_for_path(path: Path) -> Path:
    if os.path.isdir(path):
        dir_path = path
    else:
        dir_path = os.path.dirname(path)
    try:
        relative_path = (
            subprocess.check_output(
                [
                    "git",
                    "rev-parse",
                    "--show-prefix",
                ],
                cwd=os.path.realpath(dir_path),
                stderr=subprocess.DEVNULL,
            )
            .decode("utf-8")
            .strip()
        )
        # --show-toplevel doesn't work in some windows environment with posix paths,
        # like msys2, so we have to use --show-prefix instead
        git_root = os.path.abspath(
            os.path.join(dir_path, "../" * len(Path(relative_path).parts))
        )
        # call realpath to resolve symlinks, so all paths match
        return Path(os.path.realpath(git_root))
    except subprocess.CalledProcessError:
        logging.error(f"File {path} isn't part of a git project.")
        raise UserError()


def get_shared_git_root_for_paths(paths: list[Path]) -> Path:
    git_roots = set[Path]()
    for path in paths:
        git_root = _get_git_root_for_path(path)
        git_roots.add(git_root)
    if not paths:
        git_root = _get_git_root_for_path(Path(os.getcwd()))
        git_roots.add(git_root)

    if len(git_roots) > 1:
        logging.error(
            "All paths must be part of the same git project! Projects provided:"
            f" {git_roots}"
        )
        raise UserError()
    elif len(git_roots) == 0:
        logging.error("No git projects provided.")
        raise UserError()

    return git_roots.pop()


def commit(message: str) -> None:
    """
    Commit all unstaged and staged changes
    """
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", message])
