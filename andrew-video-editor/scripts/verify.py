#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from media_utils import media_summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Verify technical properties of a rendered video.")
    ap.add_argument("input")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--fps", type=float)
    ap.add_argument("--duration", type=float)
    ap.add_argument("--duration-tolerance", type=float, default=0.08)
    args = ap.parse_args()

    info = media_summary(args.input)
    failures: list[str] = []
    v = info.get("video")
    if not v:
        failures.append("no video stream")
    else:
        if args.width is not None and v.get("width") != args.width:
            failures.append(f"width {v.get('width')} != {args.width}")
        if args.height is not None and v.get("height") != args.height:
            failures.append(f"height {v.get('height')} != {args.height}")
        if args.fps is not None and (v.get("fps") is None or abs(float(v["fps"]) - args.fps) > 0.01):
            failures.append(f"fps {v.get('fps')} != {args.fps}")
    if args.duration is not None:
        d = info.get("duration")
        if d is None or abs(float(d) - args.duration) > args.duration_tolerance:
            failures.append(f"duration {d} differs from {args.duration} by > {args.duration_tolerance}s")

    print(json.dumps({"ok": not failures, "failures": failures, "probe": info}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
