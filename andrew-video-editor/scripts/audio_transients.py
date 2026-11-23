#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import statistics
import struct
import subprocess

from media_utils import require_tool


def main() -> None:
    ap = argparse.ArgumentParser(description="Detect candidate audio transients using local energy changes.")
    ap.add_argument("input")
    ap.add_argument("--sample-rate", type=int, default=16000)
    ap.add_argument("--window-ms", type=float, default=12.0)
    ap.add_argument("--min-gap-ms", type=float, default=90.0)
    ap.add_argument("--sensitivity", type=float, default=2.2, help="Higher means fewer detections")
    ap.add_argument("--limit", type=int, default=200)
    args = ap.parse_args()

    require_tool("ffmpeg")
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", args.input,
        "-vn", "-ac", "1", "-ar", str(args.sample_rate),
        "-f", "f32le", "pipe:1"
    ]
    cp = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
    raw = cp.stdout
    if len(raw) < 4:
        raise SystemExit("No decodable audio samples found")

    samples = struct.unpack("<" + "f" * (len(raw) // 4), raw)
    win = max(16, int(args.sample_rate * args.window_ms / 1000.0))
    energies: list[float] = []
    for i in range(0, len(samples) - win + 1, win):
        block = samples[i:i + win]
        rms = math.sqrt(sum(x * x for x in block) / len(block))
        energies.append(rms)

    if len(energies) < 5:
        raise SystemExit("Audio too short for transient analysis")

    # Positive energy derivative is a useful lightweight onset proxy.
    deltas = [max(0.0, energies[i] - energies[i - 1]) for i in range(1, len(energies))]
    med = statistics.median(deltas)
    mad = statistics.median(abs(x - med) for x in deltas) or 1e-9
    threshold = med + args.sensitivity * 1.4826 * mad
    hop_s = win / args.sample_rate
    min_gap = args.min_gap_ms / 1000.0

    candidates: list[dict[str, float]] = []
    max_delta = max(deltas) or 1e-9
    last_t = -1e9
    for i in range(1, len(deltas) - 1):
        d = deltas[i]
        if d < threshold:
            continue
        if d < deltas[i - 1] or d < deltas[i + 1]:
            continue
        t = (i + 1) * hop_s
        score = 100.0 * d / max_delta
        if t - last_t < min_gap:
            if candidates and score > candidates[-1]["score"]:
                candidates[-1] = {"time": round(t, 6), "score": round(score, 3)}
                last_t = t
            continue
        candidates.append({"time": round(t, 6), "score": round(score, 3)})
        last_t = t

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:args.limit]
    candidates.sort(key=lambda x: x["time"])
    print(json.dumps({
        "window_ms": args.window_ms,
        "threshold": threshold,
        "candidates": candidates
    }, indent=2))


if __name__ == "__main__":
    main()
