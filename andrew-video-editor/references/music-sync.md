# Music Sync and Rhythmic Editing

## Principle

Waveform analysis supplies candidate anchors. Editorial meaning decides whether to use them.

## Workflow

1. Detect transients with `scripts/audio_transients.py`.
2. Identify larger musical structure by listening/inspection: intro, verse, chorus, break, fill, drop, outro.
3. Mark strong structural events separately from ordinary beats.
4. Place major visual changes on structural events first.
5. Use secondary transients for internal cuts only when the desired pace supports them.
6. Test each important sync at the detected time and ±1-2 frames.

## Percussion

- Kick often supports scale/weight changes.
- Snare often supports hard cuts and flashes.
- Crash/cymbal accents often support reveals, wide shots, or brief exposure flashes.
- Fills can support accelerated cutting or a short sequence of matched actions.

These are tendencies, not rules.

## Avoid mechanical editing

Do not cut on every beat merely because beats are available. Repetition dulls impact. Preserve longer shots so faster sections have contrast.

## Music-video continuity

When synchronization and continuity conflict, first search for a nearby transient that preserves both. If none exists, continuity normally wins unless the sequence is intentionally abstract/glitch-driven.
