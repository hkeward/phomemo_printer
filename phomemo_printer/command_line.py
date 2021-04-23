import argparse, sys
from .ESCPOS_printer import Printer


def main(args):
    printer = Printer(device=args.device)

    if args.print_charset:
        printer.print_charset()
    else:
        text = args.text
        printer.print_text(text)


def cli():
    parser = argparse.ArgumentParser(
        description="Print bytes to stdout for redirection to an ESC POS printer"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--text", type=str, help="Text to print")
    group.add_argument(
        "-c",
        "--print_charset",
        help="Print full character set and exit",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-d",
        "--device",
        type=str,
        help="Device to print to [/dev/rfcomm0]",
        default="/dev/rfcomm0",
    )

    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli()
