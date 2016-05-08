import os
import sys
from StringIO import StringIO

__version__ = '1.0a'

default_app_config = 'sur.apps.SurConfig'


ROOT = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.abspath(os.path.join(ROOT, '..', 'data'))

data = lambda a: os.path.join(DATA, a)



def setup_as_lib():
    """
    this is a hackish trick.

    It setup the django enviroment through setup_environ(settings)

    Then populates the database but, instead of fixtures,
    it dumps db on disk ('disk')
    to a memory one ('default'), and then syncs the missing tables on the latter.
    """

    if ROOT not in sys.path:
        sys.path.append(ROOT)

    # import django.core.management
    from django.core.management import call_command
    from django import setup

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sur.settings")
    setup()
    call_command('migrate', verbosity=0, interactive=False)
    call_command('loaddata', data('initial_data.json'), verbosity=0, interactive=False)


if not os.environ.get('DJANGO_SETTINGS_MODULE', None):
    setup_as_lib()

    # automatically import every model
    from sur.models import *
