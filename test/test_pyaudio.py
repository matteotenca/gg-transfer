import tempfile
import unittest
import wave
from pathlib import Path

import pyaudio


# noinspection PyPep8Naming
class PyAudio(unittest.TestCase):

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
