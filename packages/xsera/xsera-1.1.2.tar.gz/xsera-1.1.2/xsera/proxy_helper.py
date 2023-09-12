from typing import Union
from aiohttp import BasicAuth
from .utils.exceptions import InvalidInputData

def create_correct_dict(proxy: Union[str, dict, list]) -> dict:
	try:
		if isinstance(proxy, str):
			proxy = {
				"http": proxy,
				"https": proxy
			}

		elif isinstance(proxy, list):
			proxy = {
				"http": proxy[0],
				"https": proxy[1]
			}

		elif isinstance(proxy, dict):
			proxy = {
				"http": proxy["http"],
				"https": proxy["https"]
			}
		else:
			raise InvalidInputData("Incorrect input data.")
		return proxy
	except (KeyError, IndexError):
		raise InvalidInputData(f'Incorrect input data.')


def create_correct_proxy_auth(username: str, password: str, aiohttp: bool = False) -> tuple or BasicAuth:
	return BasicAuth(username, password) if aiohttp else (username, password)


def create_correct_proxy(proxy: Union[str, dict, list] = None, username: str = None, password: str = None, aiohttp: bool = False) -> dict:
	if proxy:proxy = create_correct_dict(proxy)
	auth_data = create_correct_proxy_auth(username, password, aiohttp) if username and password else (None, None)
	return {"proxy": proxy, "auth": auth_data}