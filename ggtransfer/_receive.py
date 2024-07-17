import argparse
import base64
import json
import pprint
import sys
from pathlib import Path
from typing import Optional, Any, BinaryIO, TextIO, Union

import ggwave
import pyaudio

from ggtransfer._exceptions import GgIOError


def receive(args: argparse.Namespace) -> None:
    p: Optional[pyaudio.PyAudio] = None
    stream: Optional[pyaudio.Stream] = None
    instance: Optional[Any] = None
    file_path: Optional[Path] = None
    file_transfer_mode = args.file_transfer
    file = args.output
    output: Union[BinaryIO | TextIO]
    is_stdout = file is None or file == "-"

    try:
        if not is_stdout:
            file_path = Path(file)
            if file_path.is_file() and not args.overwrite:
                raise GgIOError(f"File '{file_path.absolute()}' already exists, use --overwrite to "
                                f"overwrite it.")
            if file_transfer_mode:
                output = open(file_path, "wb")
            else:
                output = open(file, "w")
        # elif file_transfer_mode:
        #     raise ValueError
        else:
            output = sys.stdout.buffer

        p = pyaudio.PyAudio()

        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=48000,
                        input=True, frames_per_buffer=4096)

        ggwave.disableLog()
        print('Listening ... Press Ctrl+C to stop', file=sys.stderr, flush=True)
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
        # pprint.pprint(ggwave.getDefaultParameters())

        i = 0
        started = False
        pieces = 0
        buf = ""
        size = 0

        while True:
            data = stream.read(4096, exception_on_overflow=False)
            res = ggwave.decode(instance, data)
            if res is not None:
                try:
                    st: str = res.decode("ascii")
                    if not started and file_transfer_mode and st.startswith("{"):
                        print("Got Header", file=sys.stderr, flush=True)
                        js = json.loads(st)
                        pieces = js["pieces"]
                        filename = js["filename"]
                        size = js["size"]
                        print(f"Filename: {filename}, Size: {size}", file=sys.stderr, flush=True)
                        print(f"Piece {i}/{pieces}", end="\r", flush=True, file=sys.stderr)
                        started = True
                    elif started and file_transfer_mode:
                        if i < pieces:
                            buf += st
                            i += 1
                            print(f"Piece {i}/{pieces} {len(buf)} B", end="\r", flush=True,
                                  file=sys.stderr)
                        else:
                            break
                    elif not file_transfer_mode:
                        print("Got message", file=sys.stderr, flush=True)
                        output.write(st.encode("ascii"))
                        output.flush()
                        # break
                except Exception as e:
                    pprint.pprint(e, stream=sys.stderr)
                    raise e
            if i >= pieces and started:
                data = base64.urlsafe_b64decode(buf)
                output.write(data)
                output.flush()
                if not is_stdout:
                    output.close()
                    stats = file_path.stat()
                    if stats.st_size != size:
                        raise GgIOError(f"File size mismatch! ({stats.st_size}, {size})")
                break
    except KeyboardInterrupt:
        return
    except GgIOError as e:
        print(e.msg, file=sys.stderr, flush=True)
        return
    finally:
        if instance is not None:
            ggwave.free(instance)
        if stream is not None:
            stream.stop_stream()
            stream.close()
        if p is not None:
            p.terminate()
