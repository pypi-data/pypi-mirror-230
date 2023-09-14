"""
Antigranular client package
"""


from .client import login

# Package version dunder
__version__ = "0.2.7"

# Package author dunder
__author__ = "Oblivious Software"

# Package * imports dunder
__all__ = ["login", "__version__", "__author__"]

"""
Raise an error if client in loaded in a non-Jupyter environment.
"""
from IPython.core.getipython import get_ipython

ipython = get_ipython()
if ipython is None:
    raise ValueError(
        "Please ensure antigranuler is loaded in a valid Jupyter environment."
    )
