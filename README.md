# gg-transfer

---
![PyPI - Status](https://img.shields.io/pypi/status/gg-transfer)
![PyPI - License](https://img.shields.io/pypi/l/gg-transfer?color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gg-transfer)


## Tool to send/receive text/binary file over audio via FSK modulation

This tool is intended to send/receive short text messages or whole binary files over audio.  
It uses `ggwave` library ([https://github.com/ggerganov/ggwave](https://github.com/ggerganov/ggwave)) to encode text messages or binary files, send
them over the audio interface, or decode them from the microphone.

It can be used - and its main purpose is - to send data through radio transceivers. See https://github.com/matteotenca/fm-transfer  

This is a shell front-end which implements the sending/receiving of bare text or whole binary files, which are encoded in Base64.

In `--file-transfer` mode, the file is opened and read all at once, then is encoded in Base64, and a header in JSON
with some info about the file itself is sent. The Base64 encoded string is split into 132 bytes/long chunks, and a 
CRC32 is added at the beginning of the block to reach the maximum block size allowed by `ggwave`, 140 bytes.
The CRCs are inserted shifted by one block to be sure the blocks arrive in the right order. At last, the checksum of the whole file
is checked against the one received in the header.

The standard behaviour is to play/record audio to/from the default audio devices.  

There are nine different protocols to send data:
```
    0 = Normal (11,17 Bytes/s - 1875 Hz to 6375 Hz)
    1 = Fast (16,76 Bytes/s - 1875 Hz to 6375 Hz)
    2 = Fastest (33,52 Bytes/s 1875 Hz to 6375 Hz)
    3 = [U] Normal (11,17 Bytes/s - 15000 Hz to 19500 Hz)
    4 = [U] Fast (16,76 Bytes/s - 15000 Hz to 19500 Hz)
    5 = [U] Fastest (33,52 Bytes/s - 15000 Hz to 19500 Hz)
    6 = [DT] Normal (3,72 Bytes/s - 1125 Hz to 2625 Hz)
    7 = [DT] Fast (5,59 Bytes/s - 1125 Hz to 2625 Hz)
    8 = [DT] Fastest (11,17 Bytes/s - 1125 Hz to 2625 Hz)
```

### Installation

```bash
$> pip install gg-transfer
```

##### Warning:
On PyPi, `ggwave-wheels` is now required, altough it provides the very same functions of the original `ggwave` package.
This is due to some glitches in the original `ggwave` install process under python `>=3.11`. `ggwave-wheels` provides 
some pre-compiled wheels for `linux x86_64`, `windows x86_64` and `macOS` platforms.

### Test installation

```bash
$> git clone https://github.com/matteotenca/gg-transfer.git
$> cd gg-transfer
$> pip install --user -e .
```

### Examples:

```
usage: gg-transfer send [-h] [-i <inputfile>] [-p {0,1,2,3,4,5,6,7,8}] [-V] [-f]

Command line utility to send/receive files/strings via ggwave library (FSK).

optional arguments:
  -h, --help            show this help message and exit
  -i <inputfile>, --input <inputfile>
                        input file (use '-' for stdin).
  -p {0,1,2,3,4,5,6,7,8}, --protocol {0,1,2,3,4,5,6,7,8}
                        protocol, 0 to 8 (defaults to 0)
                        0 = Normal (11,17 Bytes/s - 1875 Hz to 6375 Hz)
                        1 = Fast (16,76 Bytes/s - 1875 Hz to 6375 Hz)
                        2 = Fastest (33,52 Bytes/s 1875 Hz to 6375 Hz)
                        3 = [U] Normal (11,17 Bytes/s - 15000 Hz to 19500 Hz)
                        4 = [U] Fast (16,76 Bytes/s - 15000 Hz to 19500 Hz)
                        5 = [U] Fastest (33,52 Bytes/s - 15000 Hz to 19500 Hz)
                        6 = [DT] Normal (3,72 Bytes/s - 1125 Hz to 2625 Hz)
                        7 = [DT] Fast (5,59 Bytes/s - 1125 Hz to 2625 Hz)
                        8 = [DT] Fastest (11,17 Bytes/s - 1125 Hz to 2625 Hz)
  -V, --version         print version number.
  -f, --file-transfer   decode data from Base64 and use file transfer mode.
```

```
usage: gg-transfer receive [-h] [-o <outputfile>] [-w] [-n <pieces>] [-V] [-f]

Command line utility to send/receive files/strings via ggwave library (FSK).

optional arguments:
  -h, --help            show this help message and exit
  -o <outputfile>, --output <outputfile>
                        output file (use '-' for stdout).
  -w, --overwrite       overwrite output file if it exists.
  -n <pieces>, --tot-pieces <pieces>
                        receive this number of pieces and exit. Minimum is 1, default no limit.
  -V, --version         print version number.
  -f, --file-transfer   decode data from Base64 and use file transfer mode.
```
#### A simple string:

###### Sender side
```bash
$> echo "Hello world" | gg-transfer send --protocol 2
Sending data, length: 16
Piece 1/1 16 B
Time taken to encode waveform: 1.2990546226501465
Speed (payload only): 12.316649139324932 B/s
$>
```
###### Receiver side
```bash
$> gg-transfer receive
Listening ... Press Ctrl+C to stop
Hello world
[...]
```

#### A binary file:

###### Sender side
```bash
$> gg-transfer send --protocol 2 --input somefile.bin --file-transfer
Sending header, length: 71
Pieces: 2
Sending data, length: 176
Piece 2/2 176 B
Time taken to encode waveform: 6.816471338272095
Speed (size of encoded payload + CRC): 23.47255523567687 B/s
Speed (payload only): 17.311009486311693 B/s
$>
```
###### Receiver side
```bash
$> gg-transfer.exe receive --output /tmp/out.bin --file-transfer
Listening ... Press Ctrl+C to stop
Got header - Filename: .gitignore, Size: 118, CRC32: bec88992, Total pieces: 2
Piece 2/2 176 B
File received, CRC correct!
```

#### From code:

###### Sender side
```python
import ggtransfer

s = ggtransfer.Sender(protocol=2)
s.send("1234567890" * 15)
```

###### Receiver side
```python
import ggtransfer

r = ggtransfer.Receiver(file_transfer=False)
rr = r.receive()
```

### Contacts

You can contact me from my GitHub page at [https://github.com/matteotenca/gg-transfer](https://github.com/matteotenca/gg-transfer)
