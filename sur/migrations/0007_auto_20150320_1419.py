# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sur', '0006_auto_20150320_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='eosenvelope',
            name='label',
            field=models.CharField(default=b'__nolengend__', max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimentalenvelope',
            name='label',
            field=models.CharField(default=b'__nolengend__', max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
