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
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple
import sounddevice as sd # type: ignore
import ggwave # type: ignore
from ._exceptions import GgIOError, GgUnicodeError, GgArgumentsError


class Sender:

    def __init__(self, args: Optional[argparse.Namespace] = None, inputfile: Optional[str] = None,
                 protocol: int = 0, file_transfer: bool = False):

        if args is not None and isinstance(args, argparse.Namespace):
            self.protocol = args.protocol
            self.file_transfer_mode = args.file_transfer
            self.crc = self.file_transfer_mode
            self.input = args.input
        elif args is None:
            self.protocol = protocol
            self.file_transfer_mode = file_transfer
            self.crc = self.file_transfer_mode
            self.input = inputfile
        else:
            raise GgArgumentsError("Wrong set of arguments.")

        self._sample_rate = 48000

    def send(self, msg: Optional[str] = None) -> bool:
        stream: Optional[sd.RawOutputStream] = None

        try:
            # 0 = Normal
            # 1 = Fast
            # 2 = Fastest
            # 3 = [U] Normal
            # 4 = [U] Fast
            # 5 = [U] Fastest
            # 6 = [DT] Normal
            # 7 = [DT] Fast
            # 8 = [DT] Fastest

            stream = sd.RawOutputStream(dtype="float32", channels=1, samplerate=float(self._sample_rate), blocksize=4096)
            stream.start()
            if self.input is not None and self.input != "-" and msg is None:
                file_path = Path(self.input)
                if not file_path.is_file():
                    raise GgIOError(f"File {file_path.absolute()} does not exist.")
                s = file_path.stat()
                size = s.st_size
                name = file_path.name
                with open(file_path, "rb", buffering=0) as f:
                    if self.file_transfer_mode:
                        base_binary = f.read()
                        base = base64.urlsafe_b64encode(base_binary).decode("utf-8")
                        crc32_c: int = binascii.crc32(base_binary)
                        fixed_length_hex: str = f'{crc32_c:08x}'
                        ar, ln = self._get_array(base, crc=self.crc)
                        header = f'{{"pieces": {ln}, "size": {size}, "crc": "{fixed_length_hex}"}}'
                        print("Sending header, length:", len(header), flush=True, file=sys.stderr)
                        print("Pieces:", ln, flush=True, file=sys.stderr)
                        stream.write(b'0' * 4 * self._sample_rate * 1)
                        waveform = ggwave.encode(header, protocolId=self.protocol, volume=60)
                        stream.write(waveform)
                    else:
                        try:
                            base = f.read().decode("utf-8")
                            ar, ln = self._get_array(base)
                        except UnicodeDecodeError as e:
                            raise GgUnicodeError("Cannot send binary data, please use the --file-transfer option.") from e
            else:
                try:
                    if msg is not None:
                        base = msg
                    else:
                        base = sys.stdin.buffer.read().decode("utf-8")
                    ar, ln = self._get_array(base)
                    size = len(base)
                except UnicodeDecodeError as e:
                    raise GgUnicodeError("Cannot send binary data read from pipes or STDIN.") from e

            crc_size = 8 if self.file_transfer_mode else 0
            if msg is None:
                print("Sending data, length:", len(base) + (crc_size * ln), flush=True,
                      file=sys.stderr)
            q = 1
            totsize = 0
            if msg is None:
                print(f"Piece {q-1}/{ln} {totsize} B", end="\r", flush=True, file=sys.stderr)
            t = time.time()
            for piece in ar:
                waveform = ggwave.encode(piece, protocolId=self.protocol, volume=60)
                stream.write(waveform)
                totsize += len(piece)
                if msg is None:
                    print(f"Piece {q}/{ln} {totsize} B", end="\r", flush=True, file=sys.stderr)
                q += 1
            tt = time.time() - t
            stream.write(b'0' * 4 * self._sample_rate * 1)
            if msg is None:
                print(flush=True, file=sys.stderr)
                print("Time taken to encode waveform:", tt, flush=True, file=sys.stderr)
            if self.file_transfer_mode and msg is None:
                print("Speed (size of encoded payload + CRC):", len(base) / tt, "B/s", flush=True, file=sys.stderr)
            if size and msg is None:
                print("Speed (payload only):", size / tt, "B/s", flush=True, file=sys.stderr)
        except KeyboardInterrupt:
            return False
        except GgIOError as e:
            if msg is None:
                print(f"\n{e.msg}", flush=True, file=sys.stderr)
                return False
            raise e
        except GgUnicodeError as e:
            if msg is None:
                print(f"\n{e.msg}", flush=True, file=sys.stderr)
                return False
            raise e
        except GgArgumentsError as e:
            if msg is None:
                print(f"\n{e.msg}", flush=True, file=sys.stderr)
                return False
            raise e
        finally:
            if stream is not None:
                stream.stop()
                stream.close()
        return True

    @staticmethod
    def _get_array(data: str, crc: bool = False) -> Tuple[List[str], int]:
        siz = 132 if crc else 140
        ar = [data[i:i + siz] for i in range(0, len(data), siz)]
        ln = len(ar)
        crc_blocks: List[str] = []
        if crc:
            for i in range(0, ln):
                crc32: int = binascii.crc32(ar[i].encode(encoding="utf-8"))
                fixed_length_hex: str = f'{crc32:08x}'
                crc_blocks.append(fixed_length_hex)
            for i in range(1, ln):
                ar[i] = crc_blocks[i-1] + ar[i]
            ar[0] = crc_blocks[ln-1] + ar[0]
        return ar, ln
