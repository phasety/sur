import os
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.abspath(os.path.join(ROOT, '..', 'data'))

data = lambda a: os.path.join(DATA, a)

if ROOT not in sys.path:
    sys.path.append(ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")