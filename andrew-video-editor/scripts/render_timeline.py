#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import shlex
import shutil
import tempfile
from pathlib import Path

from media_utils import media_summary, require_tool, run


def atempo_chain(speed: float) -> str:
    if speed <= 0:
        raise ValueError("speed must be > 0")
    factors: list[float] = []
    x = speed
    while x > 2.0:
        factors.append(2.0)
        x /= 2.0
    while x < 0.5:
        factors.append(0.5)
        x /= 0.5
    factors.append(x)
    return ",".join(f"atempo={f:.8f}" for f in factors)


def render_segment(seg: dict, out: Path, *, width: int, height: int, fps: float, crf: int, fast: bool) -> float:
    source = Path(seg["source"])
    if not source.exists():
        raise SystemExit(f"Missing source: {source}")
    start = float(seg.get("in", 0.0))
    end = float(seg["out"])
    speed = float(seg.get("speed", 1.0))
    if start < 0 or end <= start or speed <= 0:
        raise SystemExit(f"Invalid segment range/speed: {seg}")

    info = media_summary(source)
    has_audio = info.get("audio") is not None
    duration = (end - start) / speed
    preset = "veryfast" if fast else "medium"
    vf = (
        f"trim=start={start:.9f}:end={end:.9f},"
        f"setpts=(PTS-STARTPTS)/{speed:.9f},"
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,"
        f"fps={fps:.9f},format=yuv420p"
    )

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source)]
    if has_audio:
        af = (
            f"atrim=start={start:.9f}:end={end:.9f},"
            f"asetpts=PTS-STARTPTS,{atempo_chain(speed)},"
            "aresample=48000"
        )
        cmd += ["-vf", vf, "-af", af]
    else:
        cmd += [
            "-f", "lavfi", "-t", f"{duration:.9f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-filter_complex", f"[0:v]{vf}[v]",
            "-map", "[v]", "-map", "1:a"
        ]
    cmd += [
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-shortest", "-movflags", "+faststart", str(out)
    ]
    run(cmd)
    return duration


def build_effect_filter(effects: list[dict], fps: float) -> str | None:
    filters: list[str] = []
    for effect in effects:
        if effect.get("type") != "flash":
            raise SystemExit(f"Unsupported effect type: {effect.get('type')}")
        frames = int(effect.get("frames", 0))
        if frames <= 0 or frames > 240:
            raise SystemExit(f"Invalid flash frame count: {frames}")
        if "at_frame" in effect:
            start = int(effect["at_frame"]) / fps
        else:
            start = float(effect.get("at", 0.0))
        end = start + frames / fps
        style = effect.get("style", "white")
        intensity = float(effect.get("intensity", 1.0))
        intensity = max(0.0, min(1.0, intensity))
        enable = f"gte(t\\,{start:.9f})*lt(t\\,{end:.9f})"
        if style == "white":
            filters.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=white@{intensity:.4f}:t=fill:enable='{enable}'")
        elif style == "black":
            filters.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=black@{intensity:.4f}:t=fill:enable='{enable}'")
        elif style == "exposure":
            # brightness range for eq is roughly -1..1; keep intentionally conservative.
            brightness = min(1.0, 0.85 * intensity)
            filters.append(f"eq=brightness={brightness:.4f}:enable='{enable}'")
        else:
            raise SystemExit(f"Unsupported flash style: {style}")
    return ",".join(filters) if filters else None


def main() -> None:
    ap = argparse.ArgumentParser(description="Render a deterministic hard-cut timeline with frame-duration flash effects.")
    ap.add_argument("timeline")
    ap.add_argument("--fast", action="store_true", help="Use faster preview encoding")
    ap.add_argument("--keep-temp", action="store_true")
    args = ap.parse_args()

    require_tool("ffmpeg")
    require_tool("ffprobe")
    timeline_path = Path(args.timeline)
    cfg = json.loads(timeline_path.read_text(encoding="utf-8"))
    if cfg.get("version") != 1:
        raise SystemExit("Only timeline version 1 is supported")

    output = cfg.get("output", {})
    out_path = Path(output.get("path", "final.mp4"))
    if not out_path.is_absolute():
        out_path = (timeline_path.parent / out_path).resolve()
    width = int(output.get("width", 1920))
    height = int(output.get("height", 1080))
    fps = float(output.get("fps", 30))
    crf = int(output.get("crf", 18))
    if width <= 0 or height <= 0 or fps <= 0 or not (0 <= crf <= 51):
        raise SystemExit("Invalid output geometry/fps/crf")

    segments = cfg.get("segments") or []
    if not segments:
        raise SystemExit("Timeline contains no segments")

    resolved_sources: list[Path] = []
    for seg in segments:
        src = Path(seg["source"])
        if not src.is_absolute():
            src = (timeline_path.parent / src).resolve()
        seg["source"] = str(src)
        resolved_sources.append(src)
    if any(out_path == src for src in resolved_sources):
        raise SystemExit("Output path must not overwrite a source file")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_root = Path(tempfile.mkdtemp(prefix="andrew-video-editor-"))
    try:
        parts: list[Path] = []
        total_duration = 0.0
        for i, seg in enumerate(segments):
            part = tmp_root / f"part-{i:04d}.mp4"
            total_duration += render_segment(seg, part, width=width, height=height, fps=fps, crf=crf, fast=args.fast)
            parts.append(part)

        concat_file = tmp_root / "concat.txt"
        concat_file.write_text("\n".join(f"file '{p.as_posix()}'" for p in parts) + "\n", encoding="utf-8")
        assembled = tmp_root / "assembled.mp4"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-f", "concat", "-safe", "0", "-i", str(concat_file),
             "-c", "copy", str(assembled)])

        effects = cfg.get("effects") or []
        vf = build_effect_filter(effects, fps)
        if vf:
            preset = "veryfast" if args.fast else "medium"
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                 "-i", str(assembled), "-vf", vf,
                 "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                 "-c:a", "copy", "-movflags", "+faststart", str(out_path)])
        else:
            shutil.copy2(assembled, out_path)

        summary = media_summary(out_path)
        print(json.dumps({
            "output": str(out_path),
            "planned_duration": round(total_duration, 6),
            "probe": summary,
            "fast": args.fast
        }, indent=2))
    finally:
        if args.keep_temp:
            print(f"Temporary files kept at: {tmp_root}")
        else:
            shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
