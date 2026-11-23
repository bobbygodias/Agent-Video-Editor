---
name: andrew-video-editor
description: Frame-accurate editorial video editing with FFmpeg/FFprobe. Use for intentional montage of existing footage: choosing precise cut points, music-synced edits, fast 1-4 frame flashes, continuity preservation, jump cuts, hard cuts, J/L-cut planning, speed accents, inspection around edit boundaries, intro/outro assembly, and delivery renders. Prefer editing good takes over regenerating an entire video when continuity or timing is the problem.
license: MIT
compatibility: Requires Python 3.9+ and FFmpeg/FFprobe on PATH. No cloud service or API key is required.
metadata:
  author: Bobby Dias & Andrew Vox
  version: "1.0.0"
---

# Andrew Video Editor

## Mission

Edit existing footage as an editor, not as a prompt-to-video generator. The objective is not merely to make FFmpeg run; it is to make deliberate editorial choices and then execute them reproducibly.

When several generated takes are individually good but a long generated sequence fails continuity, preserve the good takes and build the sequence through montage.

## Editorial hierarchy

Use this order when choices conflict:

1. Story and intention.
2. Continuity and subject identity.
3. Rhythm and musical phrasing.
4. Motion continuity and screen direction.
5. Technical cleanliness.
6. Effects.

An effect never rescues a bad cut. Fix the cut first.

## Mandatory workflow

1. **Probe every source.** Run `scripts/probe.py` before timing decisions. Never assume 24/25/30/60 fps, CFR/VFR, resolution, audio presence, or duration.
2. **Identify continuity locks.** Read `references/continuity.md`. Keep a short invariant list: person/wardrobe/object state, spatial direction, lighting, camera side, hand/object positions, and any user-defined continuity marker (the “pink elephant” rule).
3. **Inspect the footage.** Use `scripts/contact_sheet.py` for overview. Around every important proposed cut, use `scripts/boundary_frames.py` and inspect before/at/after frames.
4. **Find candidate sync points.** For music or percussive edits, run `scripts/audio_transients.py`. Treat detected transients as candidates, not commands. Read `references/music-sync.md`.
5. **Choose cuts in frames when precision matters.** Convert frame counts from the probed FPS. A one-frame mistake is visible in fast montage.
6. **Write a timeline.** Use `assets/timeline.example.json` as the format. Preserve source files; all decisions remain reproducible.
7. **Render a preview first.** Use `scripts/render_timeline.py ... --fast`. Inspect the output, especially boundaries and effects.
8. **Apply/adjust flashes deliberately.** Read `references/flash-effects.md`. Default to 1-4 frames; never use repeated strobing casually.
9. **Render final.** Re-run without `--fast`, then run `scripts/verify.py`.
10. **Report editorial facts.** State cut positions, flash durations in frames and milliseconds, output duration/resolution/fps, and any continuity compromise that remains.

## Cut judgement

Read `references/cuts.md` whenever the request involves rhythm, dramatic timing, or a montage rather than a simple trim.

Rules:

- Prefer a cut motivated by **action, sound, gaze, reveal, or narrative change**.
- A music transient can anchor a cut, but do not cut on every beat unless that is the intended style.
- For impact, test the exact transient and ±1-2 frames. The perceptually strongest cut may lead or lag the waveform peak slightly.
- When cutting on motion, preserve direction and let movement bridge the edit when possible.
- Avoid accidental near-matches: two shots that are almost identical but differ in hands, props, posture, or eyeline can look worse than a clearly different angle.
- J-cuts and L-cuts are editorial decisions. If dialogue or ambience should lead/follow picture, describe the intended audio overlap explicitly before executing it.

## Flash judgement

Fast flash means **frames**, not “about a tenth of a second”.

Typical starting points:

- 24/25/30 fps: 1-3 frames.
- 50/60 fps: 2-4 frames.
- Strong full-white flash: use fewer frames.
- Exposure bloom over the image: can be slightly longer than full white.

A flash at a cut can conceal a small discontinuity, but never use it to hide a major identity or geometry failure.

`render_timeline.py` supports non-destructive full-white/full-black/exposure flashes without changing timeline duration.

## Continuity protocol

Before rendering a continuity-sensitive sequence, answer internally:

- Is the same person/object visually consistent?
- Is left/right screen direction coherent?
- Does an object disappear, teleport, change hand, color, orientation, or state?
- Does camera height/axis jump unintentionally?
- Does lighting direction change without motivation?
- Is motion entering/leaving the frame compatible?
- Is there a user-defined invariant that must never change?

If a take violates a locked invariant, prefer another take or cut around the violation. Effects are a last resort.

## Tool map

- `scripts/probe.py INPUT` — media facts as JSON.
- `scripts/contact_sheet.py INPUT -o sheet.jpg` — overview sheet.
- `scripts/boundary_frames.py INPUT --at 1.25 3.70 -o frames/` — before/at/after cut frames.
- `scripts/audio_transients.py INPUT` — candidate percussive/onset timestamps.
- `scripts/render_timeline.py timeline.json --fast` — preview render.
- `scripts/render_timeline.py timeline.json` — final render.
- `scripts/verify.py OUTPUT` — final technical verification.

## Timeline format

See `assets/timeline.example.json` and `references/timeline-format.md`.

The v1 renderer intentionally focuses on reliable editorial primitives:

- frame-accurate source ranges;
- hard cuts;
- speed changes;
- normalized geometry/fps;
- full-white, full-black, and exposure flashes;
- original audio when present, silence when absent.

Do not invent unsupported timeline fields. If a requested effect is not yet implemented, explain the editorial plan and use a direct FFmpeg filter only when it can be verified visually and does not overwrite sources.

## Safety and preservation

- Never overwrite source footage.
- Use a new output path.
- Do not delete intermediates unless the user asks.
- Avoid sustained/repeated flashing that may create a photosensitivity hazard. When repeated flashes are stylistically requested, keep frequency and duration conservative and flag the issue.
- Never claim an edit “looks right” without inspecting frames or a preview.
