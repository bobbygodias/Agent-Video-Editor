#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from media_utils import media_summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Probe media and report editorially relevant facts as JSON.")
    ap.add_argument("input")
    args = ap.parse_args()
    print(json.dumps(media_summary(args.input), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
