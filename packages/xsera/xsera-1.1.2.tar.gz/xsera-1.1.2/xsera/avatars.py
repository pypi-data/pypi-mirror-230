from PIL import ImageDraw, Image
import numpy as np
import hashlib
from os import listdir
from os.path import dirname, join
from .nicknames import generate_nikcnameV1, random_seed
from random import choice
from .utils.exceptions import (
FormatError,
UnknownError,
AvatarSizeError
)

def generate_github_avatar(avatar_size: int = 240, nickname: str = None, background_color: str = "#f2f1f2", main_color: str = None, format: str = "png", dir: str = None, randomize: bool = True, save_name: str = "generated_avatar") -> str:
	path = f"{save_name}.{format}" if dir is None else f"{dir}/{save_name}.{format}"
	if nickname is None: nickname = generate_nikcnameV1()
	if randomize: nickname+=random_seed(24)
	if avatar_size % 12 != 0:
		raise AvatarSizeError('avatar size must be a multiple of 12')
	if format not in ["jpg", "png", "jpeg"]:
		raise FormatError('incorrect format (allowed: ["jpg", "png", "jpeg"])')
	bytes = hashlib.md5(nickname.encode('utf-8')).digest()
	_main_color = bytes[:3]
	_main_color = tuple(channel // 2 + 128 for channel in _main_color)
	need_color = np.array([bit == '1' for byte in bytes[3:3+9] for bit in bin(byte)[2:].zfill(8)]).reshape(6, 12)
	need_color = np.concatenate((need_color, need_color[::-1]), axis=0)
	for i in range(12):
		need_color[0, i] = 0
		need_color[11, i] = 0
		need_color[i, 0] = 0
		need_color[i, 11] = 0
	img_size = (avatar_size, avatar_size)
	block_size = avatar_size // 12 # размер квадрата
	img = Image.new('RGB', img_size, background_color)
	draw = ImageDraw.Draw(img)
	for x in range(avatar_size):
		for y in range(avatar_size):
			need_to_paint = need_color[x // block_size, y // block_size]
			if need_to_paint:
				draw.point((x, y), _main_color if not main_color else main_color)

	try:
		img.save(path)
		return path
	except Exception as e:
		raise UnknownError(f'failed to save image. ({e})')



def random_build_in_avatars(path: str, get_file: bool = True, mode: str = "rb", allowed_types: list = ["jpg", "png", "jpeg", "gif"]):
	try:
		files = listdir(path)
		while True:
			if not files:
				return {
					"path": f"No file with formats {allowed_types}",
					"file": f"No file with formats {allowed_types}"
				}
			file = choice(files)
			if file.split(".")[-1] in allowed_types:break
			else:
				files.remove(file)
		avatar_path = path+"/"+file
		return {
			"path": avatar_path,
			"file": open(avatar_path, mode) if get_file else "get_file -> False"
		}
	except Exception as e:
		raise Exception(e)
