"""Resolve engine data directories for the worldline browser."""

from __future__ import annotations

import os
from pathlib import Path


def engine_root() -> Path:
    return Path(__file__).resolve().parents[3]


def outputs_dir() -> Path:
    env = os.environ.get("LNE_OUTPUTS_DIR")
    if env:
        return Path(env)
    return engine_root() / "outputs"


def projects_dir() -> Path:
    env = os.environ.get("LNE_PROJECTS_DIR")
    if env:
        return Path(env)
    return engine_root() / "projects"


def samples_dir() -> Path:
    return engine_root() / "samples"


def static_dir() -> Path:
    return Path(__file__).resolve().parent / "static"
