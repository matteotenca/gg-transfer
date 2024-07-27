import argparse
import base64
import binascii
import sys
import time
import pyaudio
import ggwave
from pathlib import Path
from typing import List, Optional, Tuple
from ._exceptions import GgIOError, GgUnicodeError, GgArgumentsError


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


class Sender:

    def __init__(self, args: Optional[argparse.Namespace] = None, inputfile: Optional[str] = None,
                 protocol: int = 0, file_transfer: bool = False):

        if args is not None and isinstance(args, argparse.Namespace):
            self.protocol = args.protocol
            self.file_transfer_mode = args.file_transfer
            self.crc = self.file_transfer_mode
            self.input = args.input
            self._script = True
        elif args is None:
            self.protocol = protocol
            self.file_transfer_mode = file_transfer
            self.crc = self.file_transfer_mode
            self.input = inputfile
            self._script = False
        else:
            raise GgArgumentsError("Wrong set of arguments.")

    def send(self, msg: Optional[str] = None) -> None:
        p: Optional[pyaudio.PyAudio] = None
        stream: Optional[pyaudio.Stream] = None

        try:
            p = pyaudio.PyAudio()

            # 0 = Normal
            # 1 = Fast
            # 2 = Fastest
            # 3 = [U] Normal
            # 4 = [U] Fast
            # 5 = [U] Fastest
            # 6 = [DT] Normal
            # 7 = [DT] Fast
            # 8 = [DT] Fastest

            stream = p.open(format=pyaudio.paFloat32, channels=1, rate=48000, output=True,
                            frames_per_buffer=4096)
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
                        ar, ln = _get_array(base, crc=self.crc)
                        header = ('{0}"pieces": {1}, "filename": "{2}", "size": {3},'
                                  ' "crc": "{4}"{5}').format(
                            "{", str(ln), name, str(size), fixed_length_hex, "}"
                        )
                        print("Sending header, length:", len(header), flush=True, file=sys.stderr)
                        print("Pieces:", ln, flush=True, file=sys.stderr)
                        waveform = ggwave.encode(header, protocolId=self.protocol, volume=60)
                        stream.write(waveform, len(waveform) // 4)
                    else:
                        # print("Only the first 140 bytes of the file will be sent.", flush=True,
                        #       file=sys.stderr)
                        try:
                            base = f.read().decode("utf-8")
                            ar, ln = _get_array(base)
                        except UnicodeDecodeError as e:
                            raise GgUnicodeError("Cannot send binary data from file, please use "
                                                 "the --file-transfer option.") from e
            else:
                try:
                    if msg is not None:
                        base = msg
                    elif self._script:
                        # print("Only the first 140 bytes will be sent.", flush=True,
                        # file=sys.stderr)
                        base = sys.stdin.buffer.read().decode("utf-8")
                    else:
                        raise GgArgumentsError("Wrong set of arguments.")
                    ar, ln = _get_array(base)
                    size = len(base)
                except UnicodeDecodeError as e:
                    raise GgUnicodeError("Cannot send binary data read from pipes or STDIN.") from e

            # waveform = ggwave.encode("VOX", protocolId=protocol, volume=60)
            # stream.write(waveform, len(waveform) // 4)

            crc_size = 8 if self.file_transfer_mode else 0
            if self._script:
                print("Sending data, length:", len(base) + (crc_size * ln), flush=True,
                      file=sys.stderr)
            q = 1
            totsize = 0
            if self._script:
                print(f"Piece {q-1}/{ln} {totsize} B", end="\r", flush=True, file=sys.stderr)
            t = time.time()
            for piece in ar:
                # print(piece)
                waveform = ggwave.encode(piece, protocolId=self.protocol, volume=60)
                stream.write(waveform, len(waveform) // 4)
                totsize += len(piece)
                if self._script:
                    print(f"Piece {q}/{ln} {totsize} B", end="\r", flush=True, file=sys.stderr)
                q += 1
            tt = time.time() - t
            if self._script:
                print()
                print("Time taken to encode waveform:", tt, flush=True, file=sys.stderr)
            if self.file_transfer_mode and self._script:
                print("Speed (size of encoded payload + CRC):", len(base) / tt, "B/s", flush=True,
                      file=sys.stderr)
            if size and self._script:
                print("Speed (payload only):", size / tt, "B/s", flush=True, file=sys.stderr)
        except KeyboardInterrupt:
            return
        except GgIOError as e:
            if self._script:
                print(e.msg, flush=True, file=sys.stderr)
                return
            raise e
        except GgUnicodeError as e:
            if self._script:
                print(e.msg, flush=True, file=sys.stderr)
                return
            raise e
        except GgArgumentsError as e:
            if self._script:
                print(e.msg, flush=True, file=sys.stderr)
                return
            raise e
        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()
            if p is not None:
                p.terminate()
