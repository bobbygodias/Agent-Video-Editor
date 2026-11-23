# Test report — v1.0.0

Tested on 2026-09-06 with:

- FFmpeg 7.1.5
- FFprobe 7.1.5
- Python 3.13.5

## Tests passed

- Media probing on H.264/AAC MP4.
- Contact sheet generation.
- Boundary-frame extraction around edit points.
- Audio transient detection on synthetic half-second pulses.
- Two-source hard-cut timeline render.
- Frame-duration white flash as a non-destructive post-effect.
- Technical verification of H.264/AAC output at requested geometry and FPS.
- Python bytecode compilation for all bundled scripts.
- `--help` execution for all user-facing scripts.
- Agent Skills frontmatter/name/description structural checks against the published specification constraints.

## Flash test

At 30 fps, a 2-frame full-white flash was requested at the edit boundary. Frame inspection confirmed two white frames; the following frame returned to source imagery. Nominal flash duration: 66.7 ms.

## Transient test

Synthetic attacks at 0.5 s intervals were detected at approximately 0.492, 0.996, 1.500, 1.992 and 2.496 seconds. The detector is intentionally a candidate generator; editorial decisions remain with the agent/editor.
