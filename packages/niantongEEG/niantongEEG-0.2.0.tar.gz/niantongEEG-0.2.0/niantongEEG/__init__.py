import sys

if sys.version_info[:2] == (3, 6):
    from .py36.eCon import *
elif sys.version_info[:2] == (3, 7):
    from .py37.eCon import *
elif sys.version_info[:2] == (3, 8):
    from .py38.eCon import *
elif sys.version_info[:2] == (3, 9):
    from .py39.eCon import *
elif sys.version_info[:2] == (3, 10):
    from .py310.eCon import *
elif sys.version_info[:2] == (3, 11):
    from .py311.eCon import *
else:
    raise ImportError("Unsupported Python version")
