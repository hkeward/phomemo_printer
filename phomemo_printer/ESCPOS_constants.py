# Phomemo M02 Pro - 14 5-byte characters fit per line; each line is 40 bits high
MAX_CHARS_PER_LINE = 14
LINE_HEIGHT_BITS = 40

# ESC
ESC = b"\x1B"

# ESC @ - initialize printer
INITIALIZE = ESC + b"\x40"

# ESC a
## TODO can't seem to get alignment working (at least not in raster image mode); everything retains centered alignment
JUSTIFY_LEFT = ESC + b"\x61\x00"
JUSTIFY_CENTER = ESC + b"\x61\x01"
JUSTIFY_RIGHT = ESC + b"\x61\x02"

# ESC d - Print feed n
PRINT_FEED = b"\x1B\x64\x02"

## GS v 0 - Print raster image
GSV0 = b"\x1D\x76\x30\x00"

HEADER = INITIALIZE + JUSTIFY_CENTER + b"\x1f\x11\x02\x04"
FOOTER = b"\x1F\x11\x08\x1F\x11\x0E\x1f\x11\x07\x1F\x11\x09"
