import os, sys
from .pixel_sans.charset import charset
from .ESCPOS_constants import *
import socket
from PIL import Image


class Printer:
    def __init__(self, bluetooth_address, channel):
        self.s = socket.socket(
            socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
        )
        self.s.connect((bluetooth_address, channel))

    def close(self):
        """
            Close the connection to the bluetooth socket
        """
        self.s.close()

    def _print_bytes(self, bytes):
        """
            Write bytes to stdout

            Args:
                bytes (bytes): Bytes to write to stdout
        """
        self.s.send(bytes)

    def print_text(self, text):
        """
            Print text

            Args:
                text (str): Text to print
        """
        newline_separated_text_lines = []
        newline_separated_text = text.split("\n")
        for newline_chunk in newline_separated_text:
            words = newline_chunk.split(" ")
            chunk = ""
            text_lines = []
            for word in words:
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

            newline_separated_text_lines.append(text_lines)

        line_data_list = [b"" for i in range(LINE_HEIGHT_BITS)]

        self._print_bytes(HEADER)
        for index, text_lines in enumerate(newline_separated_text_lines):
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

                line_data = line_data_list.copy()
                for char in text_line:
                    try:
                        char_bytes_list = charset[char]
                    except KeyError:
                        char_bytes_list = charset["CHAR_NOT_FOUND"]
                    for index, char_bytes in enumerate(char_bytes_list):
                        line_data[index] += char_bytes

                self._print_bytes(BLOCK_MARKER)
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

    # from https://github.com/vivier/phomemo-tools
    def print_image(self, image_path):
        """
            Print an image

            Args:
                image_path (str): Path to an image file to print
        """
        image = Image.open(image_path)
        if image.width > image.height:
            image = image.transpose(Image.ROTATE_90)

        # width 384 dots
        IMAGE_WIDTH_BYTES = 70
        IMAGE_WIDTH_BITS = IMAGE_WIDTH_BYTES * 8
        image = image.resize(
            size=(IMAGE_WIDTH_BITS, int(image.height * IMAGE_WIDTH_BITS / image.width))
        )

        # black&white printer: dithering
        image = image.convert(mode="1")

        self._print_bytes(HEADER)
        for start_index in range(0, image.height, 256):
            end_index = (
                start_index + 256 if image.height - 256 > start_index else image.height
            )
            line_height = end_index - start_index

            BLOCK_MARKER = (
                GSV0
                + bytes([IMAGE_WIDTH_BYTES])
                + b"\x00"
                + bytes([line_height - 1])
                + b"\x00"
            )
            self._print_bytes(BLOCK_MARKER)

            image_lines = []
            for image_line_index in range(line_height):
                image_line = b""
                for byte_start in range(int(image.width / 8)):
                    byte = 0
                    for bit in range(8):
                        if (
                            image.getpixel(
                                (byte_start * 8 + bit, image_line_index + start_index)
                            )
                            == 0
                        ):
                            byte |= 1 << (7 - bit)
                    # 0x0a breaks the rendering
                    # 0x0a alone is processed like LineFeed by the printe
                    if byte == 0x0A:
                        byte = 0x14
                    # self._print_bytes(byte.to_bytes(1, 'little'))
                    image_line += byte.to_bytes(1, "little")

                image_lines.append(image_line)

            for l in image_lines:
                self._print_bytes(l)

        self._print_bytes(PRINT_FEED)
        self._print_bytes(PRINT_FEED)
        self._print_bytes(FOOTER)
