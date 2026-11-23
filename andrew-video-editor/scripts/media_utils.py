#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"Required tool not found on PATH: {name}")
    return path


def run(cmd: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            check=True,
            text=True,
            capture_output=capture,
        )
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            print(exc.stderr)
        raise SystemExit(f"Command failed ({exc.returncode}): {' '.join(cmd)}") from exc


def ffprobe(path: str | os.PathLike[str]) -> dict[str, Any]:
    require_tool("ffprobe")
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Input does not exist: {p}")
    cp = run([
        "ffprobe", "-v", "error",
        "-show_streams", "-show_format",
        "-of", "json", str(p)
    ], capture=True)
    return json.loads(cp.stdout)


def parse_fraction(value: str | None) -> float | None:
    if not value or value in {"0/0", "N/A"}:
        return None
    try:
        return float(Fraction(value))
    except Exception:
        try:
            return float(value)
        except Exception:
            return None


def summarize_probe(data: dict[str, Any], path: str | os.PathLike[str]) -> dict[str, Any]:
    streams = data.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fmt = data.get("format", {})
    duration = None
    try:
        duration = float(fmt.get("duration"))
    except Exception:
        pass

    fps = None
    avg_fps = None
    r_fps = None
    if v:
        avg_fps = parse_fraction(v.get("avg_frame_rate"))
        r_fps = parse_fraction(v.get("r_frame_rate"))
        fps = avg_fps or r_fps

    vfr_suspected = False
    if avg_fps and r_fps:
        vfr_suspected = abs(avg_fps - r_fps) > 0.01

    return {
        "path": str(Path(path).resolve()),
        "duration": duration,
        "video": None if not v else {
            "codec": v.get("codec_name"),
            "width": v.get("width"),
            "height": v.get("height"),
            "pixel_format": v.get("pix_fmt"),
            "fps": fps,
            "avg_fps": avg_fps,
            "r_fps": r_fps,
            "time_base": v.get("time_base"),
            "vfr_suspected": vfr_suspected,
        },
        "audio": None if not a else {
            "codec": a.get("codec_name"),
            "sample_rate": int(a["sample_rate"]) if a.get("sample_rate") else None,
            "channels": a.get("channels"),
            "channel_layout": a.get("channel_layout"),
        },
        "format": fmt.get("format_name"),
        "size_bytes": int(fmt["size"]) if fmt.get("size") else None,
    }


def media_summary(path: str | os.PathLike[str]) -> dict[str, Any]:
    return summarize_probe(ffprobe(path), path)


def frame_to_time(frame: int, fps: float) -> float:
    if frame < 0 or fps <= 0:
        raise ValueError("frame must be >= 0 and fps must be > 0")
    return frame / fps


def time_to_frame(seconds: float, fps: float) -> int:
    if seconds < 0 or fps <= 0:
        raise ValueError("seconds must be >= 0 and fps must be > 0")
    return int(round(seconds * fps))
