#!/usr/bin/env python
# coding=utf-8

import sys
import argparse
from time import sleep

from lifxlan import BLUE, COLD_WHITE, CYAN, GOLD, GREEN, LifxLAN, \
	ORANGE, PINK, PURPLE, RED, WARM_WHITE, WHITE, YELLOW

colors = {
	"red": RED,
	"orange": ORANGE,
	"yellow": YELLOW,
	"green": GREEN,
	"cyan": CYAN,
	"blue": BLUE,
	"purple": PURPLE,
	"pink": PINK,
	"white": WHITE,
	"cold_white": COLD_WHITE,
	"warm_white": WARM_WHITE,
	"gold": GOLD
}
command_description = "Change color of all LIFX lights on network for specified duration."
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description=command_description)
parser.add_argument("color", help="""color to set lights

Color should be specified via one of the predefined strings or as a four number value. The four numbers are HSBK values: Hue (0-65535), Saturation (0-65535), Brightness (0-65535), Kelvin (2500-9000).
See get_colors_all.py to read the current HSBK values from your lights.
The available predefined colors are:
""" + ", ".join(colors.keys()), nargs="+")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-d", "--duration", help="duration of color change, in seconds (default: 3.0)", type=float)
args = parser.parse_args()
duration = 3.0

if args.verbose:
	print("verbosity turned on")
if args.duration:
	duration = args.duration

def main():
	num_lights = 3

	lifxlan = LifxLAN(num_lights)

	error_message = "Please specify a valid color. Use -h or --help for more help."

	color = None
	if len(args.color) == 1:
		if args.color[0].lower() not in colors:
			print(error_message)
			sys.exit()
		else:
			color = colors[args.color[0].lower()]
	elif len(args.color) == 4:
		color = []
		for (i, value) in enumerate(args.color):
			try:
				value = int(value)
			except:
				print("Problem with {}.".format(value))
				print(error_message)
				sys.exit()
			if i == 3 and (value < 2500 or value > 9000):
				print("{} out of valid range.".format(value))
				print(error_message)
				sys.exit()
			elif value < 0 or value > 65535:
				print("{} out of valid range.".format(value))
				print(error_message)
				sys.exit()
			color.append(value)
	else:
		print(error_message)
		sys.exit()

	# Get the current state of all lights (to return to later)
	original_powers = lifxlan.get_power_all_lights()
	original_colors = lifxlan.get_color_all_lights()
	lifxlan.set_power_all_lights("on")

	# Change the color of all lights
	print(color)
	lifxlan.set_color_all_lights(color, rapid=False)

	# Keep color changed for 3 seconds
	sleep(duration);

	# Restore original state of all lights
	for light in original_powers:
		light.set_power(original_powers[light])
	for light in original_colors:
		light.set_color(original_colors[light])

# def toggle_all_lights_color(lan, interval=0.5, num_cycles=3):
#     rapid = True if interval < 1 else False
#     for i in range(num_cycles):
#         lan.set_color_all_lights(BLUE, rapid=rapid)
#         sleep(interval)
#         lan.set_color_all_lights(GREEN, rapid=rapid)
#         sleep(interval)

if __name__=="__main__":
	main()
