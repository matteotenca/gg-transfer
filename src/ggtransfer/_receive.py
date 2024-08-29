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
import argparse
import base64
import binascii
import io
import json
import sys
import time
from pathlib import Path
from typing import Optional, Any, BinaryIO, TextIO, Union
import pyaudio
import ggwave

from ._exceptions import GgIOError, GgChecksumError


class Receiver:
    def __init__(self, args: Optional[argparse.Namespace] = None,
                 output_file: Optional[str] = None, file_transfer: bool = False,
                 overwrite: bool = False, tot_pieces: int = -1) -> None:
        if args is not None:
            self.outputfile = args.output
            self.file_transfer_mode = args.file_transfer
            self.overwrite = args.overwrite
            self.tot_pieces: int = args.tot_pieces
        else:
            self.outputfile = output_file
            self.file_transfer_mode = file_transfer
            self.overwrite = overwrite
            self.tot_pieces = tot_pieces

    def receive(self, getdata: bool = True) -> Optional[str]:
        p: Optional[pyaudio.PyAudio] = None
        stream: Optional[pyaudio.Stream] = None
        instance: Optional[Any] = None
        file_path: Path = Path()
        output: Union[io.BytesIO | BinaryIO | TextIO]
        is_stdout = self.outputfile is None or self.outputfile == "-"

        try:
            if not is_stdout and not getdata:
                file_path = Path(self.outputfile)
                if file_path.is_file() and not self.overwrite:
                    raise GgIOError(f"File '{file_path.absolute()}' already exists, use "
                                    f"--overwrite to overwrite it.")
                output = open(file_path, "wb", buffering=0)
            elif not getdata:
                output = sys.stdout.buffer
            else:
                output = io.BytesIO()

            p = pyaudio.PyAudio()

            stream = p.open(format=pyaudio.paFloat32, channels=1, rate=48000,
                            input=True, frames_per_buffer=1024)

            ggwave.disableLog()
            par = ggwave.getDefaultParameters()
            # par["SampleRate"] = 44100
            # par["SampleRateInp"] = 44100
            # par["SampleRateOut"] = 44100
            # par["Channels"] = 1
            # par["Frequency"] = 44100
            # par["SampleWidth"] = 8192
            # par["SampleDepth"] = 8192
            # par["SampleType"] = 2
            # par["SampleChannels"] = 1
            # par["SampleFrequency"] = 44100
            instance = ggwave.init(par)

            i = 0
            started = False
            pieces = 0
            buf = ""
            size = 0
            last_crc: str = ""
            crc_file: str = ""
            start_time: float = 0

            if not getdata:
                print('Listening ... Press Ctrl+C to stop', file=sys.stderr, flush=True)
            while True:
                data = stream.read(1024, exception_on_overflow=False)
                res = ggwave.decode(instance, data)
                if res is not None:
                    st: str = res.decode("utf-8")
                    if not started and self.file_transfer_mode and st.startswith("{"):
                        # if not getdata:
                        #     print("Got Header", file=sys.stderr, flush=True)
                        js = json.loads(st)
                        pieces = js["pieces"]
                        filename = js["filename"]
                        size = js["size"]
                        crc_file = js["crc"]
                        if not getdata:
                            print(f"Got header - Filename: {filename}, Size: {size},"
                                  f" CRC32: {crc_file}, Total pieces: {pieces}",
                                  file=sys.stderr, flush=True)
                        if not getdata:
                            print(f"Piece {i}/{pieces} 0 B", end="\r", flush=True,
                                  file=sys.stderr)
                        started = True
                        start_time = time.time()
                    elif started and self.file_transfer_mode:
                        if i < pieces:
                            if i == 0:
                                last_crc = st[0:8]
                            else:
                                crc32_r = st[0:8]
                                crc32_c = binascii.crc32(buf[-132:].encode())
                                fixed_length_hex = f'{crc32_c:08x}'
                                if not fixed_length_hex == crc32_r:
                                    raise GgChecksumError(f"Received block's checksum ({fixed_length_hex}) is different from the expected: {crc32_r}.")
                            buf += st[8:]
                            i += 1
                            if not getdata:
                                print(f"Piece {i}/{pieces} {len(buf) + 8*i} B", end="\r",
                                      flush=True, file=sys.stderr)
                        else:
                            break
                    elif not self.file_transfer_mode:
                        # if not getdata:
                        #     print("Got message", file=sys.stderr, flush=True)
                        output.write(res)
                        output.flush()
                        i += 1
                        if getdata:
                            break
                        if i >= self.tot_pieces != -1:
                            break

                if i >= pieces and started:
                    last_block_len = len(buf) % 132
                    crc32_c = binascii.crc32(buf[-last_block_len:].encode())
                    fixed_length_hex= f'{crc32_c:08x}'
                    if not fixed_length_hex == last_crc:
                        raise GgChecksumError(f"Received block's checksum ({fixed_length_hex}) is different from the expected: {last_crc}.")
                    decoded_data = base64.urlsafe_b64decode(buf)
                    crc32_c = binascii.crc32(decoded_data)
                    fixed_length_hex = f'{crc32_c:08x}'
                    if not fixed_length_hex == crc_file:
                        raise GgChecksumError(f"File's checksum ({fixed_length_hex}) is different from the expected: {crc_file}.")
                    output.write(decoded_data)
                    output.flush()
                    if not getdata and self.file_transfer_mode:
                        elapsed_time = time.time() - start_time
                        print("Speed (size of encoded payload + CRC):", len(buf) / elapsed_time, "B/s", flush=True,
                              file=sys.stderr)
                        if size:
                            print("Speed (payload only):", size / elapsed_time, "B/s", flush=True, file=sys.stderr)
                    if not is_stdout and not getdata:
                        output.close()
                        stats = file_path.stat()
                        if stats.st_size != size:
                            raise GgIOError(f"File size mismatch! ({stats.st_size}, {size})")
                        if not getdata:
                            print("\nFile received, CRC correct!", file=sys.stderr, flush=True)
                    break
        except KeyboardInterrupt:
            return None
        except GgChecksumError as e:
            print(e.msg, file=sys.stderr, flush=True)
            return None
        except GgIOError as e:
            print(e.msg, file=sys.stderr, flush=True)
            return None
        finally:
            if instance is not None:
                ggwave.free(instance)
            if stream is not None:
                stream.stop_stream()
                stream.close()
            if p is not None:
                p.terminate()
        if getdata and isinstance(output, io.BytesIO):
            ret: str = output.getvalue().decode("utf-8")
            return ret
        return None
