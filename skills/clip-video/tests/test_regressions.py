"""Focused regression checks. Run with the project's .venv Python."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from clipper import fetch
from clipper.edit import write_ass
from clipper.plan import build


class CacheTests(unittest.TestCase):
    def test_same_filename_and_modified_sources_get_distinct_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a, b = root / 'a' / 'video.mp4', root / 'b' / 'video.mp4'
            a.parent.mkdir()
            b.parent.mkdir()
            a.write_bytes(b'first')
            b.write_bytes(b'second')
            with patch.object(fetch, 'OUTPUT', root / 'output'), patch.object(fetch, 'probe', return_value={'duration': 10}):
                first, _ = fetch.local_source(a)
                repeat, _ = fetch.local_source(a)
                second, _ = fetch.local_source(b)
                a.write_bytes(b'updated source with different size')
                changed, _ = fetch.local_source(a)
            self.assertEqual(first, repeat)
            self.assertEqual(len({first, second, changed}), 3)

    def test_interrupted_extraction_never_creates_a_cache_hit(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / 'audio16k.wav'

            def fail(*args):
                Path(args[-1]).write_bytes(b'partial')
                raise RuntimeError('decoder interrupted')

            with patch.object(fetch, 'ffmpeg', side_effect=fail):
                with self.assertRaises(RuntimeError):
                    fetch.to_wav16k('source.mp4', dst)
            self.assertFalse(dst.exists())

            def succeed(*args):
                Path(args[-1]).write_bytes(b'complete')

            with patch.object(fetch, 'ffmpeg', side_effect=succeed):
                fetch.to_wav16k('source.mp4', dst)
            self.assertEqual(dst.read_bytes(), b'complete')


class CaptionTests(unittest.TestCase):
    def test_zero_start_and_literal_subtitle_text(self):
        meta = {'duration': 1.5, 'fps': 30, 'words': [
            {'w': r'Literal\N{text}', 's': 0, 'e': 0.5},
            {'w': 'end.', 's': 0.7, 'e': 1.1}], 'shots': [], 'splices': []}
        plan = build(meta, {'text': '#FFFFFF', 'accent': '#FFD60A', 'outline': '#000000'},
                     {'zoom': False, 'sfx': 'none', 'uppercase': False})
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / 'caption.ass'
            write_ass(plan, dst)
            text = dst.read_text()
        dialogue = [line for line in text.splitlines() if line.startswith('Dialogue:')]
        self.assertTrue(dialogue[0].startswith('Dialogue: 0,0:00:00.00,'))
        self.assertIn('Literal/N(text)', text)
        self.assertNotIn(r'Literal\N', text)


if __name__ == '__main__':
    unittest.main()
