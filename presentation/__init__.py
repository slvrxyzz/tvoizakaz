import importlib
import sys

_module = importlib.import_module("src.presentation")

# propagate attributes to keep dir() working on the alias
globals().update(_module.__dict__)

# register alias in sys.modules so that submodules resolve correctly
sys.modules[__name__] = _module

