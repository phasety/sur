import os
import sys
from StringIO import StringIO
import sqlite3

ROOT = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.abspath(os.path.join(ROOT, '..', 'data'))

data = lambda a: os.path.join(DATA, a)


def setup_db():
    if ROOT not in sys.path:
        sys.path.append(ROOT)

    import django.core.management
    from django.core.management import call_command
    import settings
    django.core.management.setup_environ(settings)

    # Read database to tempfile
    con = sqlite3.connect(data('dev.db'))
    tempfile = StringIO()
    for line in con.iterdump():
        tempfile.write('%s\n' % line)
    con.close()
    tempfile.seek(0)

    from django.db import connection
    # Use in memory and import from tempfile
    connection.cursor().executescript(tempfile.read())

    call_command('syncdb')

setup_db()