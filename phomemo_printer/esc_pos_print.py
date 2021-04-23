import os, sys
from .font.font import characters as font
from .esc_pos_constants import *


def _print_bytes(device, bytes):
    """
        Write bytes to stdout

        Args:
            bytes (bytes): Bytes to write to stdout
    """
    # with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        # stdout.write(bytes)
    with os.fdopen(os.open(device, os.O_WRONLY), "wb", closefd=False) as dev:
        dev.write(bytes)

def print_text(device, text):
    """
        Print text

        Args:
            text (str): Text to print
    """
    text = text.split(" ")
    chunk = ""
    text_lines = []
    for word in text:
        delimiter = "" if len(chunk) in [0, MAX_CHARS_PER_LINE] else " "
        if len(word) + len(chunk) + len(delimiter) > MAX_CHARS_PER_LINE:
            # flush the chunk and make a new chunk

            if len(chunk) != 0 and len(chunk) <= MAX_CHARS_PER_LINE:
                text_lines.append(chunk)
                chunk = word
            else:
                # single word longer than MAX_CHARS_PER_LINE
                word_hunks = [
                    chunk[i : i + MAX_CHARS_PER_LINE - 1]
                    for i in range(0, len(chunk), MAX_CHARS_PER_LINE - 1)
                ]
                for word_hunk in word_hunks[:-2]:
                    text_lines.append(word_hunk + "-")
                if len(word_hunks[-1]) == 1:
                    text_lines.append(word_hunks[-2] + word_hunks[-1])
                else:
                    text_lines.append(word_hunks[-2] + "-")
                    chunk = word_hunks[-1]
                delimiter = "" if len(chunk) in [0, MAX_CHARS_PER_LINE] else " "
                if len(word) + len(chunk) + len(delimiter) > MAX_CHARS_PER_LINE:
                    text_lines.append(chunk)
                    chunk = word
                else:
                    chunk = chunk + delimiter + word
        else:
            chunk = chunk + delimiter + word
    # flush last chunk
    if len(chunk) <= MAX_CHARS_PER_LINE:
        text_lines.append(chunk)
    else:
        word_hunks = [
            chunk[i : i + MAX_CHARS_PER_LINE - 1]
            for i in range(0, len(chunk), MAX_CHARS_PER_LINE - 1)
        ]
        for word_hunk in word_hunks[:-2]:
            text_lines.append(word_hunk + "-")
        if len(word_hunks[-1]) == 1:
            text_lines.append(word_hunks[-2] + word_hunks[-1])
        else:
            text_lines.append(word_hunks[-2] + "-")
            text_lines.append(word_hunks[-1])

    line_data_list = [b"" for i in range(LINE_HEIGHT_BITS)]

    _print_bytes(device, HEADER)
    for text_line in text_lines:
        bytes_per_line = len(text_line) * 5
        if bytes_per_line > MAX_CHARS_PER_LINE * 5:
            raise SystemExit(
                "Line too long to print; failed to split correctly?\n[{}]".format(
                    text_line
                )
            )

        BLOCK_MARKER = (
            GSV0
            + bytes([bytes_per_line])
            + b"\x00"
            + bytes([LINE_HEIGHT_BITS])
            + b"\x00"
        )
        _print_bytes(device, BLOCK_MARKER)

        line_data = line_data_list.copy()
        for char in text_line:
            char_bytes_list = font[char]
            for index, char_bytes in enumerate(char_bytes_list):
                line_data[index] += char_bytes

        for bit_line in line_data:
            _print_bytes(device, bit_line)

    _print_bytes(device, PRINT_FEED)
    _print_bytes(device, PRINT_FEED)
    _print_bytes(device, FOOTER)


def print_charset(device):
    """
        Print all printable characters
    """
    char_string = "".join(list(font.keys()))
    char_string_split = " ".join(
        [
            char_string[i : i + MAX_CHARS_PER_LINE]
            for i in range(0, len(char_string), MAX_CHARS_PER_LINE)
        ]
    )
    print_text(device, char_string_split)
