from os import system
from typing import Union, Any, Iterable
from pprint import pprint
from hueprint.types import EColour, EEffect
from hueprint.utils import _format_text
system("color")  # This, for initialization purposes, forces colour to be displayed in the console window.


def cprint(text: Union[str, Any], colour: EColour = None, effect: EEffect = None) -> None:
	"""
	A simple wrapper of the built-in `print` function with enhanced support for colours and effects.
	:param text: The text to print. If the argument is not of type `str`, the object will be converted to a string via a `__str__` call.
	:param colour: The colour to use when printing.
	:param effect: The text effect to use when printing.
	"""
	print(_format_text(text, colour, effect))


def sprint(text: Union[str, Any]) -> None:
	"""
	Prints text stylized as a 'Success' (e.g. "Success: Operation Complete.").
	The colour used is `EColour.LIGHT_GREEN`.
	:param text: The text to print. If the argument is not of type `str`, the object will be converted to a string via a `__str__` call.
	"""
	print(EColour.LIGHT_GREEN.value + text + EColour.NONE.value)


def nprint(text: Union[str, Any]) -> None:
	"""
	Prints text stylized as a 'Notification' (e.g. "Notification: Done loading 6,900 resources!").
	The colour used is `EColour.LIGHT_BLUE`.
	:param text: The text to print. If the argument is not of type `str`, the object will be converted to a string via a `__str__` call.
	"""
	print(EColour.LIGHT_BLUE.value + text + EColour.NONE.value)


def wprint(text: Union[str, Any]) -> None:
	"""
	Print stylized as a 'Warning' (e.g. "Warning: Attempted to mark for delete a file that is already marked for delete.").
	The colour used is `EColour.YELLOW`.
	:param text: The text to print. If the argument is not of type `str`, the object will be converted to a string via a `__str__` call.
	"""
	print(EColour.YELLOW.value + text + EColour.NONE.value)


def eprint(text: Union[str, Any]) -> None:
	"""
	Prints text stylized as an 'Error' (e.g. "File does not exist.").
	The colour used is `EColour.LIGHT_RED`.
	:param text: The text to print. If the argument is not of type `str`, the object will be converted to a string via a `__str__` call.
	"""
	print(EColour.LIGHT_RED.value + text + EColour.NONE.value)


def iprint(iterable: Iterable):
	"""
	Wrapper function to the generic pprint function. Good for printing containers/collections and other iterables.
	:param iterable: Iterable (generally a collection or container) to print.
	"""
	pprint(iterable)
