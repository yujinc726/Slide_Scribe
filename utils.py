import os
import json
import glob
import shutil
from typing import List, Any

import streamlit as st

from github_storage import (
    github_enabled,
    list_lectures,
    list_json,
    load_json,
)

__all__ = [
    "get_user_base_dir",
    "load_lecture_names",
    "list_json_files_for_lecture",
    "load_records_from_json",
    "ensure_directory",
    "delete_lecture",
]

# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------

def _user_id() -> str:
    """Return the current user id stored in `st.session_state`."""
    return st.session_state.get("user_id", "anonymous") or "anonymous"


def get_user_base_dir() -> str:
    """Local base directory (relative to project root) for the current user."""
    return os.path.join("timer_logs", _user_id())


def ensure_directory(path: str) -> None:
    """Create *path* (and parents) if it does not yet exist."""
    os.makedirs(path, exist_ok=True)

# ---------------------------------------------------------------------------
# Listing helpers
# ---------------------------------------------------------------------------

def load_lecture_names() -> List[str]:
    """Return the list of lecture names for the current user.

    • When GitHub integration is enabled (`github_enabled()` returns `True`),
      the list is read from the remote repository using `github_storage.list_lectures`.
    • Otherwise, the list is produced from the local file-system under
      `timer_logs/<user_id>`.
    """
    if github_enabled():
        return list_lectures(_user_id())

    base_dir = get_user_base_dir()
    if not os.path.exists(base_dir):
        return []
    return sorted(
        [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    )


def list_json_files_for_lecture(lecture: str, *, names_only: bool = True) -> List[str]:
    """Return JSON files for *lecture*.

    Parameters
    ----------
    lecture : str
        Lecture name.
    names_only : bool, default ``True``
        When *True* only the filename (e.g. ``2024-05-04_153034.json``) is
        returned.  When *False* the full path / GitHub reference is returned
        (e.g. ``github://<lecture>/<filename>`` or
        ``timer_logs/<user_id>/<lecture>/<filename>``).
    """
    if not lecture:
        return []

    if github_enabled():
        files = list_json(_user_id(), lecture)
        if names_only:
            return files
        return [f"github://{lecture}/{f}" for f in files]

    directory = os.path.join(get_user_base_dir(), lecture)
    if not os.path.exists(directory):
        return []
    paths = sorted(glob.glob(os.path.join(directory, "*.json")), reverse=True)
    if names_only:
        return [os.path.basename(p) for p in paths]
    return paths

# ---------------------------------------------------------------------------
# Loading records
# ---------------------------------------------------------------------------

def load_records_from_json(ref: str | None) -> List[Any]:
    """Load timer records from *ref* which can be either local path or
    a GitHub reference (``github://lecture/filename``).
    """
    if not ref:
        return []

    if ref.startswith("github://"):
        lecture, filename = ref.replace("github://", "", 1).split("/", 1)
        return load_json(_user_id(), lecture, filename)

    try:
        with open(ref, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except Exception:
        return []

# ---------------------------------------------------------------------------
# Deletion helpers
# ---------------------------------------------------------------------------

def delete_lecture(lecture: str) -> None:
    """Delete *lecture* both locally (if present) and on GitHub (if enabled)."""
    # local removal
    local_dir = os.path.join(get_user_base_dir(), lecture)
    if os.path.exists(local_dir):
        try:
            shutil.rmtree(local_dir)
        except Exception:
            pass

    # GitHub removal
    if not github_enabled():
        return

    # Import here to avoid circular import issues
    from github_storage import _get_repo  # pylint: disable=import-outside-toplevel, protected-access

    repo = _get_repo()
    if repo is None:
        return

    base_path = f"timer_logs/{_user_id()}/{lecture}"
    try:
        contents = repo.get_contents(base_path)
    except Exception:
        return  # path does not exist remotely

    for item in contents:
        if item.type == "file":
            try:
                repo.delete_file(item.path, f"Delete {item.path}", item.sha)
            except Exception:
                continue

    # After all files are deleted, the directory implicitly disappears in Git. 