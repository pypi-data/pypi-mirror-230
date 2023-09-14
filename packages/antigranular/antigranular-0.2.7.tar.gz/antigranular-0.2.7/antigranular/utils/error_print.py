"""
eprint to print to stderr instead of stdout.
"""

import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
