import os
import sys

__here__ = os.path.dirname(os.path.abspath(sys.argv[0]))
data = lambda a: os.path.join(__here__, a)
