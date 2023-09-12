
from .colors import Colors
from .utils.utils import colors_names
from .avatars import generate_github_avatar, random_build_in_avatars
from .nicknames import generate_nikcnameV1, generate_nikcnameV2
from os import system as s

from .proxy_helper import (
	create_correct_dict,
	create_correct_proxy_auth,
	create_correct_proxy
)

from .utils.exceptions import (
InvalidInputData,
FormatError,
UnknownError,
AvatarSizeError
)


__title__ = 'xsera'
__author__ = 'Xsarz'
__license__ = 'MIT'
__copyright__ = 'Copyright 2023 Xsarz'
__version__ = '1.1.2'

from json import loads
from requests import get
try:__newest__ = loads(get("https://pypi.org/pypi/xsera/json").text)["info"]["version"]
except:__newest__=__version__
if __version__ != __newest__:
	s('cls || clear')
	print(Colors.orange_3+f'{__title__} made by {__author__}\nPlease update the library. Your version: {__version__}  A new version:{__newest__}'+Colors.color_end)