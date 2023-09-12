from random import choice
from string import ascii_uppercase, ascii_lowercase
from random import randint, choice, randrange
from os.path import dirname, join
from .utils.utils import (
vowels,
consonants,
replacement_letters,
nouns, adjectives
)

def random_seed(number: int = 4) -> str:
	return ''.join(choice(ascii_uppercase) for i in range(number))


def generate_nikcnameV1(length: int = None, first_symbol: str = '', replacing_vowels: bool = True, use_hissing: bool = True) -> str:
	if not first_symbol:first_symbol=choice(ascii_lowercase)
	for i in range(length if length else  randint(3, 9) -len(first_symbol)):
		new = choice(vowels) if first_symbol[-1] in consonants else choice(consonants)
		if replacing_vowels or use_hissing:
			if new in replacement_letters.keys() and replacing_vowels:first_symbol+=choice([replacement_letters.get(new, new), new])
			elif first_symbol[-1] in ('c', 's') and use_hissing:first_symbol+=choice(["h", new])
			else:first_symbol+=new
		else:first_symbol+=new
	return first_symbol



def generate_nikcnameV2(use_num: bool = False) -> str:
	adjective = choice(adjectives)
	noun = choice(nouns).capitalize()
	num = str(randrange(10)) if use_num else ''
	return adjective + noun + num
