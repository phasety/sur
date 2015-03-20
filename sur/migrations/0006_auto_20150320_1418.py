# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sur', '0005_auto_20150319_1351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eosenvelope',
            name='label',
        ),
        migrations.RemoveField(
            model_name='experimentalenvelope',
            name='label',
        ),
    ]
