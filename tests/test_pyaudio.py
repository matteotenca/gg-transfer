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
import wave
from pathlib import Path

import pyaudio


# noinspection PyPep8Naming
class PyAudio(unittest.TestCase):

    @unittest.skip("skipping test_record...")
    def test_record(self) -> None:
        CHUNK = 1024
        FORMAT = pyaudio.paInt32
        CHANNELS = 1
        RATE = 48000
        RECORD_SECONDS = 20
        out_file = Path(tempfile.gettempdir()).absolute().joinpath('test.wav')
        wf: wave.Wave_write
        with wave.open(str(out_file), 'w') as wf:

            p = pyaudio.PyAudio()
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)

            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)
            print(f'Recording {RECORD_SECONDS} secs into {out_file}...')
            for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
                wf.writeframes(stream.read(CHUNK))
            print('Done')
            stream.stop_stream()
            stream.close()
            p.terminate()
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
