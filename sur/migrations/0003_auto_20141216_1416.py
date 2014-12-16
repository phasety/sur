# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sur', '0002_auto_20141208_2321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compound',
            name='vc',
            field=models.FloatField(null=True, verbose_name=b'Critical Volume', blank=True),
            preserve_default=True,
        ),
    ]
