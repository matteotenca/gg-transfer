import argparse
from ggtransfer._send import send
from ggtransfer._receive import receive


def _main() -> None:

    parser = argparse.ArgumentParser(prog="gg-transfer", description="Command line utility to "
                                                                     "moduleate/demodulate data "
                                                                     "via gg-wave.", )
    subparsers = parser.add_subparsers(required=True)

    sender = subparsers.add_parser(
        "send", help="modulate data into audio signal.")
    sender.add_argument(
        "-i", "--input", help="input file (use '-' for stdin).")
    sender.add_argument(
        "-p", "--protocol", help="protocol, 0 to 8 (defaults to 0).", default="0",
        type=int, choices=range(0, 9))
    sender.add_argument(
        "-f", "--file-transfer",
        help="encode data in base64 and use file transfer mode.",
        action="store_true", default=False)
    sender.set_defaults(command="send")

    receiver = subparsers.add_parser(
        "receive", help="demodulate data from audio signal.")
    receiver.add_argument(
        "-o", "--output", help="output file (use '-' for stdout).")
    receiver.add_argument(
        "-f", "--file-transfer",
        help="decode data from base64 and use file transfer mode.",
        action="store_true", default=False)
    receiver.add_argument(
        "-w", "--overwrite",
        help="overwrite output file if it exists.",
        action="store_true", default=False)

    receiver.set_defaults(command="receive")

    args: argparse.Namespace = parser.parse_args()

    if args.command == "send":
        send(args)
    elif args.command == "receive":
        receive(args)


if __name__ == '__main__':
    _main()
