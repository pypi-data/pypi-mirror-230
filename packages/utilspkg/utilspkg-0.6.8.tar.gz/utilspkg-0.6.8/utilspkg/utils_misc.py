import re
from typing import Optional


def extract_integer(text: str, round: bool = False) -> Optional[int]:
    """
    Extracts the first number from the provided text and returns it as an integer.
    If no number is found, returns None.
    If 'round' is True, rounds the number to the nearest integer before returning.
    """
    number = extract_float(text)
    if number is not None:
        return int(round(number)) if round else int(number)
    else:
        return None


def extract_float(text: str) -> Optional[float]:
    """
    Searches for the first number in the provided text and returns it as a float.
    If no number is found, returns None.
    """
    match = re.search(r'\b\d+\b', text)
    return float(match.group()) if match else None
