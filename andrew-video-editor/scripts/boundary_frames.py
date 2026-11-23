#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from media_utils import media_summary, require_tool, run


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract before/at/after frames around proposed edit points.")
    ap.add_argument("input")
    ap.add_argument("--at", type=float, nargs="+", required=True, help="Cut times in seconds")
    ap.add_argument("-o", "--output-dir", default="boundary-frames")
    ap.add_argument("--radius", type=int, default=2, help="Frames before/after each cut")
    args = ap.parse_args()

    require_tool("ffmpeg")
    info = media_summary(args.input)
    video = info.get("video")
    if not video or not video.get("fps"):
        raise SystemExit("Video stream/FPS not available")
    fps = float(video["fps"])
    duration = float(info.get("duration") or 0)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for cut_index, t in enumerate(args.at, 1):
        for offset in range(-args.radius, args.radius + 1):
            ts = max(0.0, min(duration, t + offset / fps))
            label = f"cut{cut_index:02d}_t{t:.3f}_f{offset:+d}_{ts:.6f}.png"
            out = out_dir / label
            # Accurate seek after input. One frame only.
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                 "-i", args.input, "-ss", f"{ts:.9f}", "-frames:v", "1", str(out)])
    print(out_dir.resolve())


if __name__ == "__main__":
    main()
