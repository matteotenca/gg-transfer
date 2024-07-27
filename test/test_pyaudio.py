import unittest
import wave

import pyaudio


# noinspection PyPep8Naming
class PyAudio(unittest.TestCase):

    def test_record(self) -> None:
        CHUNK = 1024
        FORMAT = pyaudio.paInt32
        CHANNELS = 1
        RATE = 48000
        RECORD_SECONDS = 20
        wf: wave.Wave_write = wave.open(r'r:\output.wav', 'w')
        if wf:
            p = pyaudio.PyAudio()
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)

            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

            print(f'Recording {RECORD_SECONDS} secs...')
            for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
                wf.writeframes(stream.read(CHUNK))
            print('Done')

            stream.close()
            p.terminate()
            wf.close()
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
