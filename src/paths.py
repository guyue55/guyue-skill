"""Resolve Guyue-owned user data paths without coupling them to an install."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping


def _resolved(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def guyue_home(
    *,
    environ: Mapping[str, str] | None = None,
    user_home: Path | None = None,
) -> Path:
    """Return the private Guyue root, defaulting to ``~/.guyue``."""
    env = os.environ if environ is None else environ
    configured = str(env.get("GUYUE_HOME", "")).strip()
    if configured:
        return _resolved(Path(configured))
    home = user_home if user_home is not None else Path.home()
    return _resolved(home / ".guyue")


def private_memory_dir(
    *,
    environ: Mapping[str, str] | None = None,
    user_home: Path | None = None,
) -> Path:
    """Return the writable private memory directory.

    ``GUYUE_MEMORY_DIR`` remains a narrow compatibility override. New
    installations should configure the complete root with ``GUYUE_HOME``.
    """
    env = os.environ if environ is None else environ
    configured = str(env.get("GUYUE_MEMORY_DIR", "")).strip()
    if configured:
        return _resolved(Path(configured))
    return guyue_home(environ=env, user_home=user_home) / "knowledge" / "memory"


def discovery_cache_file(
    *,
    environ: Mapping[str, str] | None = None,
    user_home: Path | None = None,
) -> Path:
    return (
        guyue_home(environ=environ, user_home=user_home)
        / "cache"
        / "discovery"
        / "skills-index.json"
    )


def migration_state_dir(
    *,
    environ: Mapping[str, str] | None = None,
    user_home: Path | None = None,
) -> Path:
    return guyue_home(environ=environ, user_home=user_home) / "state" / "migrations"


def ensure_private_directory(path: Path, *, private_root: Path | None = None) -> None:
    """Create a private directory and harden every component below its root."""
    destination = _resolved(path)
    root = _resolved(private_root) if private_root is not None else guyue_home()
    try:
        relative = destination.relative_to(root)
    except ValueError:
        missing: list[Path] = []
        current = destination
        while not current.exists():
            missing.append(current)
            if current.parent == current:
                break
            current = current.parent
        for directory in reversed(missing):
            directory.mkdir(exist_ok=True, mode=0o700)
            directory.chmod(0o700)
        destination.chmod(0o700)
        return

    current = root
    for component in (Path(), *relative.parts):
        current = root if component == Path() else current / component
        current.mkdir(exist_ok=True, mode=0o700)
        current.chmod(0o700)


def legacy_private_memory_dir(install_root: Path) -> Path:
    return install_root.resolve(strict=False) / ".guyue_memory" / "local"
