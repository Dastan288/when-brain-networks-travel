"""Shared helpers: config loading, seeding, paths.

Every script in data/ and src/ imports from here so that paths and seeds
are defined exactly once (config/config.yaml).
"""

from __future__ import annotations

import hashlib
import os
import random
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config(path: Path | str = CONFIG_PATH) -> dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    # Resolve relative paths against the project root
    for key, val in cfg["paths"].items():
        p = Path(val)
        cfg["paths"][key] = str(p if p.is_absolute() else PROJECT_ROOT / p)
    return cfg


def set_seed(seed: int) -> None:
    """Fix every RNG we use. Call at the top of every entry point."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def md5sum(path: Path | str, chunk: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


ABIDE_STRATEGIES = ("filt_noglobal", "filt_global", "nofilt_noglobal", "nofilt_global")


def abide_strategy(cfg: dict, strategy: str | None = None) -> str:
    s = strategy or cfg["abide"]["strategy"]
    if s not in ABIDE_STRATEGIES:
        raise ValueError(f"unknown ABIDE strategy {s!r}; choose from {ABIDE_STRATEGIES}")
    return s


def abide_tag(cfg: dict, strategy: str | None = None) -> str:
    """Dataset tag used in file names: 'abide' for the primary strategy, 'abide-<strategy>' otherwise."""
    s = abide_strategy(cfg, strategy)
    return "abide" if s == cfg["abide"]["strategy"] else f"abide-{s}"


def abide_dirs(cfg: dict, strategy: str | None = None) -> dict:
    """Return the on-disk layout nilearn uses for ABIDE PCP for one preprocessing strategy."""
    raw = Path(cfg["paths"]["raw"])
    a = cfg["abide"]
    s = abide_strategy(cfg, strategy)
    base = raw / "ABIDE_pcp"
    return {
        "base": base,
        "phenotypic": base / a["phenotypic_csv"],
        "derivatives": base / a["pipeline"] / s,
        "strategy": s,
        "band_pass_filtering": s.startswith("filt_"),
        "global_signal_regression": s.endswith("_global"),
        "tag": abide_tag(cfg, s),
        "cache": {atlas: Path(cfg["paths"]["raw"]).parent / "cache" / f"abide_{s}_rois_{atlas}.npz"
                  for atlas in ("aal", "cc200")},
    }
