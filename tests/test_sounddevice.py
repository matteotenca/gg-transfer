"""
        gg-transfer - a tool to transfer files encoded in audio via FSK modulation
        Copyright (C) 2024 Matteo Tenca

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import tempfile
import unittest
from pathlib import Path
import sounddevice as sd

# noinspection PyPep8Naming
class TestSoundDevice(unittest.TestCase):

    @unittest.skip("skipping test_record...")
    def test_record(self) -> None:
        try:
            import soundfile as sf
        except (ImportError, ModuleNotFoundError):
            self.fail("soundfile module not found")
        CHUNK: int = 1024
        FORMAT: str = "float32"
        CHANNELS: int = 1
        RATE: float = float(48000)
        RECORD_SECONDS: int = 5
        out_file = Path(tempfile.gettempdir()).absolute().joinpath('test.wav')
        with sf.SoundFile(out_file, "wb", samplerate=int(RATE), channels=1, format='WAV', subtype="FLOAT") as wf:
            with sd.RawInputStream(dtype=FORMAT, channels=CHANNELS, samplerate=RATE, blocksize=CHUNK) as stream:
                print(f'Recording {RECORD_SECONDS} secs into {out_file}...')
                for _ in range(0, int(RATE // CHUNK * RECORD_SECONDS)):
                    data, overflow = stream.read(CHUNK)
                    wf.buffer_write(data, "float32")
                print('Done')
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
