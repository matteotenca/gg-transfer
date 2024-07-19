import argparse
import base64
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

import ggwave
import pyaudio

from ggtransfer._exceptions import GgIOError, GgUnicodeError


def _get_array(data: bytes | str) -> Tuple[List[bytes | str], int]:
    ar = [data[i:i + 140] for i in range(0, len(data), 140)]
    ln = len(ar)
    return ar, ln


def send(args: argparse.Namespace) -> None:
    p: Optional[pyaudio.PyAudio] = None
    stream: Optional[pyaudio.Stream] = None

    try:
        p = pyaudio.PyAudio()

        protocol = args.protocol
        file_transfer_mode = args.file_transfer

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
        if args.input is not None and args.input != "-":
            file = args.input
            file_path = Path(file)
            if not file_path.is_file():
                raise GgIOError(f"File {file_path.absolute()} does not exist.")
            s = file_path.stat()
            size = s.st_size
            name = file_path.name
            if file_transfer_mode:
                with open(file, "rb") as f:
                    base = base64.urlsafe_b64encode(f.read()).decode("ascii")
                    ar, ln = _get_array(base)
                    header = '{0}"pieces": {1}, "filename": "{2}", "size": {3}{4}'.format(
                        "{", str(ln), name, str(size), "}"
                    )
                    print("Sending header, length:", len(header), flush=True, file=sys.stderr)
                    waveform = ggwave.encode(header, protocolId=protocol, volume=60)
                    stream.write(waveform, len(waveform) // 4)
            else:
                with open(file, "r") as f:
                    print("Only the first 140 bytes will be sent.", flush=True, file=sys.stderr)
                    try:
                        base = f.read(140)
                        ar, ln = _get_array(base)
                    except UnicodeDecodeError:
                        raise GgUnicodeError("Cannot send binary data as is, please use the "
                                             "--file-transfer option.")
        else:
            try:
                print("Only the first 140 bytes will be sent.", flush=True, file=sys.stderr)
                base = sys.stdin.buffer.read(140).decode("ascii")
                ar, ln = _get_array(base)
            except UnicodeDecodeError:
                raise GgUnicodeError("Cannot send binary data read from pipes or STDIN.")

        # waveform = ggwave.encode("VOX", protocolId=protocol, volume=60)
        # stream.write(waveform, len(waveform) // 4)

        print("Sending data, length:", len(base), flush=True, file=sys.stderr)
        q = 1
        totsize = 0
        t = time.time()
        for piece in ar:
            totsize += len(piece)
            print(f"Piece {q}/{ln} {totsize} B", end="\r", flush=True, file=sys.stderr)
            waveform = ggwave.encode(piece, protocolId=protocol, volume=60)
            stream.write(waveform, len(waveform) // 4)
            q += 1

        tt = time.time() - t
        print()
        print("Time taken to encode waveform:", tt, flush=True, file=sys.stderr)
        print("Speed:", len(base) / tt, "B/s", flush=True, file=sys.stderr)
    except KeyboardInterrupt:
        return
    except GgIOError as e:
        print(e.msg, flush=True, file=sys.stderr)
        return
    except GgUnicodeError as e:
        print(e.msg, flush=True, file=sys.stderr)
        return
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        if p is not None:
            p.terminate()
