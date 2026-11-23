"""Tests for the public command-line video editor; no personal media used."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "andrew-video-editor"
sys.path.insert(0, str(ROOT / "scripts"))
from media_utils import frame_to_time, time_to_frame  # noqa: E402
from render_timeline import atempo_chain, build_effect_filter  # noqa: E402


class EditorUnitTests(unittest.TestCase):
    def test_frame_conversion(self):
        self.assertAlmostEqual(frame_to_time(15, 30), 0.5)
        self.assertEqual(time_to_frame(0.5, 30), 15)
        with self.assertRaises(ValueError):
            time_to_frame(-1, 30)

    def test_audio_speed_chain(self):
        self.assertIn("atempo=", atempo_chain(1.0))
        self.assertGreaterEqual(atempo_chain(4.0).count("atempo="), 2)
        with self.assertRaises(ValueError):
            atempo_chain(0)

    def test_flash_filter(self):
        self.assertIn("drawbox", build_effect_filter([
            {"type": "flash", "at_frame": 15, "frames": 2, "style": "white"}
        ], 30))
        self.assertIsNone(build_effect_filter([], 30))
        with self.assertRaises(SystemExit):
            build_effect_filter([{"type": "unsupported", "frames": 2}], 30)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg unavailable")
    def test_render_smoke(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            for color, name in [("red", "first.mp4"), ("blue", "second.mp4")]:
                subprocess.run([
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
                    "-i", f"color=c={color}:size=160x120:rate=30:duration=1",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(p / name),
                ], check=True)
            timeline = {"version": 1, "output": {"path": "out.mp4", "width": 160,
                          "height": 120, "fps": 30, "crf": 28},
                        "segments": [{"source": "first.mp4", "in": 0, "out": 0.5},
                                     {"source": "second.mp4", "in": 0, "out": 0.5}],
                        "effects": [{"type": "flash", "at_frame": 15, "frames": 2, "style": "white"}]}
            (p / "timeline.json").write_text(json.dumps(timeline), encoding="utf-8")
            subprocess.run([sys.executable, str(ROOT / "scripts/render_timeline.py"),
                            str(p / "timeline.json"), "--fast"], check=True, capture_output=True)
            subprocess.run([sys.executable, str(ROOT / "scripts/verify.py"), str(p / "out.mp4"),
                            "--width", "160", "--height", "120", "--fps", "30",
                            "--duration", "1.0", "--duration-tolerance", "0.10"],
                           check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
