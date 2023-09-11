from enum import Enum


class EColour(str, Enum):
	"""An enumerator of colours."""
	NONE = '\033[0m'
	BLACK = '\033[30m'
	RED = '\033[31m'
	GREEN = '\033[32m'
	ORANGE = '\033[33m'
	BLUE = '\033[34m'
	PURPLE = '\033[35m'
	CYAN = '\033[36m'
	LIGHT_GREY = '\033[37m'
	DARK_GREY = '\033[90m'
	LIGHT_RED = '\033[91m'
	LIGHT_GREEN = '\033[92m'
	YELLOW = '\033[93m'
	LIGHT_BLUE = '\033[94m'
	PINK = '\033[95m'
	LIGHT_CYAN = '\033[96m'


class EEffect(str, Enum):
	"""An enumerator of text effects."""
	NONE = '\033[0m'
	BOLD = '\033[01m'
	ITALIC = '\033[03m'
	DISABLE = '\033[02m'
	UNDERLINE = '\033[04m'
	REVERSE = '\033[07m'
	STRIKETHROUGH = '\033[09m'
	INVISIBLE = '\033[08m'
