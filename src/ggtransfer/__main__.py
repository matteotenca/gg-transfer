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
from typing import Any
from ._send import Sender
from ._receive import Receiver
from ._exceptions import GgArgumentsError
from . import __version__


class GgHelpFormatter(argparse.RawTextHelpFormatter):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def format_help(self) -> str:
        help_msg = self._root_section.format_help()
        if help_msg:
            help_msg = self._long_break_matcher.sub('\n\n', help_msg)
            help_msg = help_msg.strip('\n') + '\n'
        return help_msg


def is_postive_int(val: str) -> int:
    # try:
    val_int = int(val)
    if val_int > 0:
        return val_int
    raise argparse.ArgumentTypeError("number of pieces must be a positive integer.")


def _main() -> None:

    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(prog="gg-transfer",
                                     # formatter_class=GgHelpFormatter,
                                     description="Command line utility to send/receive "
                                                 "files/strings via ggwave library (FSK).")
    parser.add_argument(
        "-V", "--version",
        help="print version number.",
        action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(required=True, title="commands",
                                       help="send or receive data.")

    # noinspection PyTypeChecker
    sender = subparsers.add_parser(
        "send", help="modulate data into audio signal.", formatter_class=GgHelpFormatter,
        description="Command line utility to send/receive files/strings via ggwave library (FSK).")
    sender.add_argument(
        "-i", "--input", help="input file (use '-' for stdin).", metavar="<inputfile>")
    sender.add_argument(
        "-p", "--protocol", help="protocol, 0 to 8 (defaults to %(default)s)\n"
                                 "0 = Normal (11,17 Bytes/s - 1875 Hz to 6375 Hz)\n"
                                 "1 = Fast (16,76 Bytes/s - 1875 Hz to 6375 Hz)\n"
                                 "2 = Fastest (33,52 Bytes/s 1875 Hz to 6375 Hz)\n"
                                 "3 = [U] Normal (11,17 Bytes/s - 15000 Hz to 19500 Hz)\n"
                                 "4 = [U] Fast (16,76 Bytes/s - 15000 Hz to 19500 Hz)\n"
                                 "5 = [U] Fastest (33,52 Bytes/s - 15000 Hz to 19500 Hz)\n"
                                 "6 = [DT] Normal (3,72 Bytes/s - 1125 Hz to 2625 Hz)\n"
                                 "7 = [DT] Fast (5,59 Bytes/s - 1125 Hz to 2625 Hz)\n"
                                 "8 = [DT] Fastest (11,17 Bytes/s - 1125 Hz to 2625 Hz)",
        default=0,
        type=int,
        choices=range(0, 9)
    )
    sender.add_argument(
        "-f", "--file-transfer",
        help="encode data in Base64 and use file transfer mode.",
        action="store_true", default=False)
    sender.set_defaults(command="send")

    # noinspection PyTypeChecker
    receiver = subparsers.add_parser(
        "receive", help="demodulate data from audio signal.", formatter_class=GgHelpFormatter,
        description="Command line utility to send/receive files/strings via ggwave library (FSK).")
    receiver.add_argument(
        "-o", "--output", help="output file (use '-' for stdout).", metavar="<outputfile>")
    receiver.add_argument(
        "-f", "--file-transfer",
        help="decode data from Base64 and use file transfer mode.",
        action="store_true", default=False)
    receiver.add_argument(
        "-w", "--overwrite",
        help="overwrite output file if it exists.",
        action="store_true", default=False)
    receiver.add_argument(
        "-n", "--tot-pieces",
        help="receive this number of pieces and exit. Minimum is 1, default no limit.",
        default=-1, type=is_postive_int)

    receiver.set_defaults(command="receive")

    args: argparse.Namespace = parser.parse_args()

    if args.command == "send":
        Sender(args).send()
    elif args.command == "receive":
        Receiver(args).receive(getdata=False)
    else:
        raise GgArgumentsError("No such command.")


if __name__ == '__main__':
    _main()
