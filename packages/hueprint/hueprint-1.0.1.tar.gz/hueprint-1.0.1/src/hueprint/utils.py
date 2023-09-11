from typing import Union, Any, Iterable
from hueprint.types import EColour, EEffect


def _format_text(text: Union[str, Any], colour: EColour = None, effect: EEffect = None) -> str:
	"""
	Adds colour and effects flags to a string such that it will be formatted with these when passed to the print() function.\n
	:param text: The string to format. If the argument is not of type `str`, the object will be converted to a string via a `__str__` call.
	:param colour: The colour to use when printing.
	:param effect: The text effect to use when printing.
	:return: The input string with the relevant colour and effect flags added.
	"""
	# A User Sequences/Collections should provide its `data` property for printing.
	to_print: str = text.__str__()
	if isinstance(colour, EColour):
		to_print = colour.value + to_print
	if isinstance(effect, EEffect):
		to_print = effect.value + to_print
	return to_print + EColour.NONE
