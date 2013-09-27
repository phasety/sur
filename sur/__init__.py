import os
import sys
from StringIO import StringIO


ROOT = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.abspath(os.path.join(ROOT, '..', 'data'))

data = lambda a: os.path.join(DATA, a)


def setup_db():
    """
    this is a hackish trick.

    It setup the django enviroment throght setup_environ(settings)

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

    from django.db import connections
    connections['disk'].cursor()    # to construct the connection instance
    con = connections['disk'].connection
    tempfile = StringIO()
    for line in con.iterdump():
        tempfile.write('%s\n' % line)
    tempfile.seek(0)

    # Use in memory and import from tempfile
    connections['default'].cursor().executescript(tempfile.read())

    call_command('syncdb', verbosity=0)

setup_db()
