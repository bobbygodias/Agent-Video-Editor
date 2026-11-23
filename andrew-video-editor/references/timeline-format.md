# Timeline Format v1

```json
{
  "version": 1,
  "output": {
    "path": "final.mp4",
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "crf": 18
  },
  "segments": [
    {"source": "shot-a.mp4", "in": 0.50, "out": 2.75, "speed": 1.0},
    {"source": "shot-b.mp4", "in": 1.10, "out": 3.20, "speed": 1.0}
  ],
  "effects": [
    {"type": "flash", "at": 2.25, "frames": 2, "style": "white", "intensity": 1.0}
  ]
}
```

## output

- `path`: required destination. Must not equal any source path.
- `width`, `height`: target frame size; default 1920x1080.
- `fps`: constant output FPS; default 30.
- `crf`: x264 quality, default 18; lower is higher quality.

## segments

- `source`: input media path.
- `in`: start time in seconds, inclusive.
- `out`: end time in seconds, exclusive.
- `speed`: optional. 1.0 is normal, 2.0 is twice as fast, 0.5 is half speed.

Segments are assembled in listed order with hard cuts.

## effects / flash

- `at`: time in seconds in the assembled output.
- `at_frame`: alternative to `at`; frame index in output timeline.
- `frames`: positive integer duration.
- `style`: `white`, `black`, or `exposure`.
- `intensity`: 0..1. For white/black it controls opacity; for exposure it controls brightness increase.

Flashes are post-effects and do not change duration.
