import os
import sys
from StringIO import StringIO
from pkg_resources import get_distribution, DistributionNotFound
import os.path

try:
    _dist = get_distribution('sur')
except DistributionNotFound:
    __version__ = 'dev'
else:
    __version__ = _dist.version


default_app_config = 'sur.apps.SurConfig'


ROOT = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.abspath(os.path.join(ROOT, '..', 'data'))

data = lambda a: os.path.join(DATA, a)


def setup_database():
    """
    this is a hackish trick.

    It setup the django enviroment through setup_environ(settings)

    Then populates the database but, instead of fixtures,
    it dumps db on disk ('disk')
    to a memory one ('default'), and then syncs the missing tables on the latter.
    """
    from django.core.management import call_command
    from django import setup
    setup()
    call_command('migrate', verbosity=0, interactive=False)
    call_command('loaddata', data('initial_data.json'), verbosity=0, interactive=False)


if not os.environ.get('DJANGO_SETTINGS_MODULE', None):
    if ROOT not in sys.path:
        sys.path.append(ROOT)

    # import django.core.management
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sur.settings")

    # automatically import every model
    from sur.models import *
