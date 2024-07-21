# gg-transfer

[![License: GPLv3](https://img.shields.io/badge/license-GPLv3+-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.txt)

## Tool to send/receive text/binary file over audio via FSK modulation

This small tool is intended to send/receive short text messages or whole binary files over audio.  
It uses `ggwave` library ([https://github.com/ggerganov/ggwave](https://github.com/ggerganov/ggwave)) to encode text messages or binary files, send
them over the audio interface, or decode them from the microphone.  

This is a shell front-end which implements the sending/receiving of bare text or whole binary files, which are encoded in Base64.

When in file transfer mode, it reads the file, encode it in Base64, and sends a header in JSON with some info about the file itself.
Then splits the Base64-encoded string in 140 chars-long blocks, and send them: `ggwave` encodes each block into audio 
and `gg-transfer` plays them to the default audio interface.  
  
The receieving part, while in file transfer mode, waits to receive the header, then reads the right number of blocks, assembles them
in a single Base64 string and decodes it into binary.

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

### Test installation

```bash
$> git clone https://github.com/matteotenca/gg-transfer.git
$> cd gg-transfer
$> pip install --user -e .
```


### Examples:

```
usage: gg-transfer send [-h] [-i <inputfile>] [-p {0,1,2,3,4,5,6,7,8}] [-f]


options:
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
  -f, --file-transfer   encode data in Base64 and use file transfer mode.
```

```
usage: gg-transfer receive [-h] [-o <outputfile>] [-f] [-w]


options:
  -h, --help            show this help message and exit
  -o <outputfile>, --output <outputfile>
                        output file (use '-' for stdout).
  -f, --file-transfer   decode data from Base64 and use file transfer mode.
  -w, --overwrite       overwrite output file if it exists.
```
#### A simple string:

###### Sender side
```bash
$> echo "Hello world" | gg-transfer send --protocol 2
Only the first 140 bytes will be sent.
Sending data, length: 16
Piece 1/1 16 B
Time taken to encode waveform: 1.3006865978240967
Speed: 12.301195404616463 B/s
$>
```
###### Receiver side
```bash
$> gg-transfer receive
Listening ... Press Ctrl+C to stop
Got message
"Hello world"
[...]
```

#### A binary file:

###### Sender side
```bash
$> gg-transfer send --protocol 2 --input somefile.bin --file-transfer
Sending header, length: 57
Sending data, length: 644
Piece 5/5 644 B
Time taken to encode waveform: 23.129117012023926
Speed: 27.84369155403596 B/s
$>
```
###### Receiver side
```bash
$> gg-transfer.exe receive --output /tmp/out.bin --file-transfer
Listening ... Press Ctrl+C to stop
Got Header
Filename: somefile.bin, Size: 482
Piece 5/5 644 B
```

### Contacts

You can contact me from my GitHub page at [https://github.com/matteotenca/gg-transfer](https://github.com/matteotenca/gg-transfer)
