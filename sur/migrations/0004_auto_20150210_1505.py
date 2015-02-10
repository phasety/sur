# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sur', '0003_auto_20141216_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='eosflash',
            name='v',
            field=models.FloatField(null=True, verbose_name=b'Volume of the flash'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimentalflash',
            name='v',
            field=models.FloatField(null=True, verbose_name=b'Volume of the flash'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eosflash',
            name='p',
            field=models.FloatField(null=True, verbose_name=b'Pressure of the flash'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experimentalflash',
            name='p',
            field=models.FloatField(null=True, verbose_name=b'Pressure of the flash'),
            preserve_default=True,
        ),
    ]
