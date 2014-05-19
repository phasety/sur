import os
import sys
from StringIO import StringIO


ROOT = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.abspath(os.path.join(ROOT, '..', 'data'))

data = lambda a: os.path.join(DATA, a)


def copydb(dbfrom='disk', dbto='default'):
    """read the database and return a tempfile"""
    from django.db import connections


    connections[dbfrom].cursor()    # to construct the connection instance
    con = connections[dbfrom].connection
    tempfile = StringIO()
    for line in con.iterdump():
        tempfile.write('%s\n' % line)
    tempfile.seek(0)
    if dbto:
        connections[dbto].cursor().executescript(tempfile.read())
    tempfile.seek(0)
    return tempfile



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

    import django.core.management
    from django.core.management import call_command
    import settings
    django.core.management.setup_environ(settings)

    copydb('disk', 'default')
    call_command('syncdb', verbosity=0, interactive=False)


if not os.environ.get('DJANGO_SETTINGS_MODULE', None):
    setup_as_lib()

    # automatically import every model
    from sur.models import *
    from sur.plots import *