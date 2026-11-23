# Andrew Video Editor

Open Agent Skill for frame-accurate editorial video montage using local FFmpeg/FFprobe.

The skill focuses on editorial judgement — where and why to cut, musical sync, continuity, frame-level inspection, and very short flash effects — while FFmpeg performs the mechanics.

## Requirements

- Python 3.9+
- FFmpeg and FFprobe on PATH

No cloud service or API key is required.

## Install

Copy the entire `andrew-video-editor/` directory into the skills directory used by your Agent-Skills-compatible client. The folder name must remain `andrew-video-editor` because the Agent Skills specification requires it to match the `name` in `SKILL.md`.

## First test

```bash
python3 scripts/probe.py your-video.mp4
python3 scripts/contact_sheet.py your-video.mp4 -o sheet.jpg
```

For an edit, copy `assets/timeline.example.json`, replace the source paths and cut times, then run:

```bash
python3 scripts/render_timeline.py timeline.json --fast
python3 scripts/verify.py intro-preview.mp4
```

## License

MIT. See `LICENSE`.
