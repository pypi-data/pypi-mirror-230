"""
There are functions to work with strings.
"""

import re


def to_camelcase(s):
    """
    Converts string to camelcase.
    """
    s = re.sub(r'([A-Z])', r' \1', s)
    s = re.sub(r'\W+', ' ', s)
    return ''.join(map(str.title, s.split()))


def to_snakecase(s):
    """
    Converts string to snakecase.
    """
    s = re.sub(r'([A-Z])', r' \1', s)
    return re.sub(r'[^a-zA-Z0-9]+', '_', s).lower().strip('_')


def to_cebabcase(s):
    """
    Converts string to cebabcase.
    """
    s = re.sub(r'([A-Z])', r' \1', s)
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).lower().strip('-')
