# Phomemo printer - python utilities to allow printing text from the phomemo printer

I have not been able to print text to the Phomemo printer using standard ESC/POS print commands; to work around this, this library allows printing of text as a raster bit image.

Various methods to connect to the Phomemo printer and print images are excellently described [here](https://github.com/vivier/phomemo-tools).

Tools were tested on a Phomemo M02 Pro printer.


## Requirements

- python3
- bluetooth connection tools (if connecting to the printer over bluetooth)


## Installation

```
sudo python3 setup.py install
```

This will create and install a CLI called `phomemo_printer` on your PATH.


## Usage

### Connecting to the printer (bluetooth)

*For non-bluetooth connection methods, see [https://github.com/vivier/phomemo-tools](https://github.com/vivier/phomemo-tools).*

The Debian package `bluez` provides the utilities needed to scan for and connect to the printer via bluetooth.


1. Find the bluetooth printer's MAC address

```
$ hcitool scan

Scanning ...
	00:AA:13:41:11:A5	M02 Pro
```

2. Determine which channel to connect to the device on

Format: `sdptool browse {MAC_address}`

```
$ sdptool browse 00:AA:13:41:11:A5

Browsing 00:AA:13:41:11:A5 ...
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

3. Connect to the printer

Format: `sudo rfcomm connect {device} {MAC_address} {channel}`. The device can be any `/dev/rfcomm` device that is not in use.

```
$ sudo rfcomm connect /dev/rfcomm0 00:AA:13:41:11:A5 6

Connected /dev/rfcomm0 to  on channel 6
Press CTRL-C for hangup
```


### Sending text to the printer

#### CLI

Format: `sudo phomemo_printer -d {device} -t "text to print"`

```
sudo phomemo_printer -d /dev/rfcomm0 -t "Hello world"
```


#### Module import

Note that scripts that print to devices in `/dev/` will require superuser permissions to run.

```python3
from phomemo_printer.ESCPOS_printer import Printer

printer = Printer("/dev/rfcomm0")
printer.print_text("Hello world")
```
