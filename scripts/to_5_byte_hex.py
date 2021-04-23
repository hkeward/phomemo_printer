#!/usr/bin/env python3

import argparse
import re

fourbit_to_hex = {
		'0000': '0',
		'0001': '1',
		'0010': '2',
		'0011': '3',
		'0100': '4',
		'0101': '5',
		'0110': '6',
		'0111': '7',
		'1000': '8',
		'1001': '9',
		'1010': 'A',
		'1011': 'B',
		'1100': 'C',
		'1101': 'D',
		'1110': 'E',
		'1111': 'F'
	}

def main(args):
	binary_digits = args.binary
	character = args.character

	if len(binary_digits) < 8:
		raise SystemExit("Must provide 8 binary digits; {} provided.".format(len(binary_digits)))

	hex = []
	for binary in binary_digits:
		if not re.match('^[01]{8}$', binary):
			raise SystemExit("binary string should be 8 digits long and contain only the digits 0 or 1")

		five_byte_hex_chars = []
		five_byte_binary = ''.join([bit * 5 for bit in binary])
		for start_index in range(0, len(five_byte_binary), 8):
			first_digit = fourbit_to_hex[five_byte_binary[start_index:start_index + 4]]
			second_digit = fourbit_to_hex[five_byte_binary[start_index + 4:start_index + 8]]
			five_byte_hex_chars.append("\\x{}{}".format(first_digit, second_digit))

		five_byte_hex = ["b'{}'".format(''.join(five_byte_hex_chars))] * 5
		hex.append(',\n\t\t'.join(five_byte_hex))

	print("CHAR_{} = [\n\t\t{}\n\t]".format(character, ',\n\t\t'.join(hex)))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Convert 1-byte binary to 5-byte hex")

	parser.add_argument(
		"-b",
		"--binary",
		type=str,
		help="Binary byte to convert to 5-byte hex",
		required=True,
		nargs='+',
	)
	parser.add_argument(
		"-c",
		"--character",
		type=str,
		help="Character being converted",
		required=True,
	)

	args = parser.parse_args()
	main(args)
