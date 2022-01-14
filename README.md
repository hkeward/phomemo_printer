# Phomemo printer - python utilities to allow printing text and images from the Phomemo printer

I have not been able to print text to the Phomemo printer using standard ESC/POS print commands (if your printer does work with these commands, you should use the library [here](https://github.com/python-escpos/python-escpos)). To work around this, this library allows printing of text as a raster bit image. It also allows for actual image files to be printed directly.

This currently only allows connection to the printer via bluetooth; various methods to connect to the Phomemo printer and print images are excellently described [here](https://github.com/vivier/phomemo-tools) if bluetooth does not suit your needs.

Tools were tested on a Phomemo M02 Pro printer.


## Requirements

- python3
- bluetooth interrogation tools (e.g. via the `bluez` package)


## Installation

```
sudo python3 setup.py install
```

This will create a CLI called `phomemo_printer` on your PATH.


Alternatively, install via pip:

```
python3 -m pip install phomemo_printer
```


## Usage

The printer is connected to over bluetooth. To connect, the bluetooth address and channel must be determined.


### Finding the printer's bluetooth address and channel

The Debian package `bluez` provides the utilities needed to scan for and connect to the printer via bluetooth.


1. Find the printer's bluetooth address

The printer should be powered on and not connected to any computer or app.

```
$ hcitool scan

Scanning ...
	00:AA:13:41:11:A5	M02 Pro
```

The bluetooth address should be in the format xx:xx:xx:xx:xx:xx. If more than one bluetooth device is discovered, look for one with the name of your printer.


2. Determine which channel to connect to the device on

Format: `sdptool browse bluetooth_address`

```
$ sdptool browse 00:AA:13:41:11:A5

Browsing  ...
Service Name: SerialPort
Service RecHandle: 0x1000f
Service Class ID List:
  "Serial Port" (0x1101)
Protocol Descriptor List:
  "L2CAP" (0x0100)
  "RFCOMM" (0x0003)
    Channel: 6
Profile Descriptor List:
  "Serial Port" (0x1101)
    Version: 0x0102
```


### Sending text to the printer

#### Via CLI

Format: `phomemo_printer -a bluetooth_address -c bluetooth_channel -t "text to print"`

```
phomemo_printer -a 00:AA:13:41:11:A5 -c 6 -t "Hello world"
```


#### Via module import

```python3
from phomemo_printer.ESCPOS_printer import Printer

printer = Printer(bluetooth_address="00:AA:13:41:11:A5", channel=6)
printer.print_text("Hello world")
printer.close()
```


### Sending images to the printer

Format: `phomemo_printer -a bluetooth_address -c bluetooth_channel -i "/path/to/image.png"`
