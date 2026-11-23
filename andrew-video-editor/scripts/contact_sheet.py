#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path

from media_utils import media_summary, require_tool, run


def main() -> None:
    ap = argparse.ArgumentParser(description="Create an evenly sampled visual contact sheet.")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", default="contact-sheet.jpg")
    ap.add_argument("--frames", type=int, default=12, help="Number of frames to sample (default 12)")
    ap.add_argument("--columns", type=int, default=4)
    ap.add_argument("--thumb-width", type=int, default=480)
    args = ap.parse_args()

    require_tool("ffmpeg")
    info = media_summary(args.input)
    if not info.get("video"):
        raise SystemExit("Input has no video stream")
    duration = info.get("duration")
    if not duration or duration <= 0:
        raise SystemExit("Could not determine input duration")
    if args.frames < 1 or args.columns < 1:
        raise SystemExit("--frames and --columns must be positive")

    rows = math.ceil(args.frames / args.columns)
    # Slightly avoid exact first/last frame, which are frequently black or partial GOP boundaries.
    sample_fps = args.frames / duration
    vf = (
        f"fps={sample_fps:.9f},"
        f"scale={args.thumb_width}:-2,"
        f"drawtext=text='%{{pts\\:hms}}':x=12:y=h-th-12:fontsize=22:"
        f"fontcolor=white:box=1:boxcolor=black@0.55,"
        f"tile={args.columns}x{rows}:nb_frames={args.frames}:padding=6:margin=6"
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-i", args.input, "-vf", vf, "-frames:v", "1", str(out)])
    print(out.resolve())


if __name__ == "__main__":
    main()
