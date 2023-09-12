from os import system
from .utils.utils import *

import sys
from time import sleep


class Colors:
	objects = dict()
	for num, color in enumerate(colors_names):
		c = f'{ESC}{num}{END}'
		vars()[color] = c
		objects[color] = c
	for color in background_colors_names:
		c = f"\033[{background_colors_names[color]}{END}"
		vars()[color] =  c
		objects[color] = c

	for color in styles:
		c = f"\033[{styles[color]}{END}"
		vars()[color] =  c
		objects[color] = c

	color_reset = '\033[39m'
	bg_reset = '\033[49m'
	color_end = COLOR_END
	objects["color_reset"] = color_reset
	objects["bg_reset"] = bg_reset
	objects["color_end"] = COLOR_END




	def show_all(self) -> None:
		self.debug_color()
		for code in colors_names:
			print(self.color(code=code, text=f"[{code}]"))
		for code in background_colors_names:
			print(self.color(code=code, text=f"[{code}]"))
		for code in styles:
			print(self.color(code=code, text=f"[{code}]"))


	def get_all(self) -> dict:
		return list(self.objects.keys())


	def debug_color(self) -> None:
		system('clear || cls')
		print(self.reset, self.bg_reset)
		system('clear || cls')


	def sleeping_blink_once(self, text: str, wait: float = 0.5) -> None:
		sys.stdout.write(f'\r{text}')
		sleep(wait)
		sys.stdout.write(f'\r{" "*len(text)}')
		sleep(wait)

	def sleeping_blink(self, text: str, repetitions: int = 1, wait: float = 0.5) -> None:
		for x in range(0,repetitions):
			self.sleeping_blink_once(text=text, wait=wait)
		print()


	def color(self, code: str, text: str = None) -> str:
		if code in self.objects.keys():
			return f"{self.objects[code]}{text}{COLOR_END}" if text else self.objects[code]
		return text



	def hex(self, color: str, text: str = None) -> str:
		if len(color) == 4:
			color = '#'+color[1]*2+color[2]*2+color[3]*2
		for hex_color, hexcolor in hex_colors.items():
			if hexcolor == color:
				return hex_color
		r, g, b = (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
		cube = lambda x: x * x
		f = lambda hex_val, ref : cube(int(hex_val, 16) - ref)
		min_cube_d = cube(0xFFFFFF)
		nearest = '15'
		for k, h in hex_colors.items():
			cube_d = f(h[1:3], r) + f(h[3:5], g) + f(h[5:7], b)
			if cube_d < min_cube_d:
				min_cube_d = cube_d
				nearest = k

		return f'{ESC}{nearest}{END}{text}{COLOR_END}' if text else f'{ESC}{nearest}{END}'