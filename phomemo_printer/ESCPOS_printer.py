import os, sys
from .pixel_sans.charset import charset
from .ESCPOS_constants import *


class Printer:
    def __init__(self, device):
        self.device = device

    def _print_bytes(self, bytes):
        """
            Write bytes to stdout

            Args:
                bytes (bytes): Bytes to write to stdout
        """
        with os.fdopen(os.open(self.device, os.O_WRONLY), "wb", closefd=False) as dev:
            dev.write(bytes)

    def print_text(self, text):
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

        self._print_bytes(HEADER)
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
            self._print_bytes(BLOCK_MARKER)

            line_data = line_data_list.copy()
            for char in text_line:
                char_bytes_list = charset[char]
                for index, char_bytes in enumerate(char_bytes_list):
                    line_data[index] += char_bytes

            for bit_line in line_data:
                self._print_bytes(bit_line)

        self._print_bytes(PRINT_FEED)
        self._print_bytes(PRINT_FEED)
        self._print_bytes(FOOTER)

    def print_charset(self):
        """
            Print all printable characters
        """
        char_string = "".join(list(charset.keys()))
        char_string_split = " ".join(
            [
                char_string[i : i + MAX_CHARS_PER_LINE]
                for i in range(0, len(char_string), MAX_CHARS_PER_LINE)
            ]
        )
        self.print_text(char_string_split)
