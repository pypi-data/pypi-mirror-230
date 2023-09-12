
class InvalidInputData(Exception):
	"""
	Perhaps you specified the wrong argument or the wrong type of the argument
	"""
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)


class FormatError(Exception):
	"""
	You specified the wrong file format
	"""
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)


class FormatError(Exception):
	"""
	You specified the wrong file format
	"""
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)


class UnknownError(Exception):
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)



class AvatarSizeError(Exception):
	"""
	Invalid avatar size
	"""
	def __init__(*args, **kwargs):
		Exception.__init__(*args, **kwargs)