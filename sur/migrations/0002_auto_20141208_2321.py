# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sur', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eosflash',
            name='beta',
        ),
        migrations.RemoveField(
            model_name='experimentalflash',
            name='beta',
        ),
        migrations.AddField(
            model_name='eosflash',
            name='beta_mol',
            field=models.FloatField(null=True, verbose_name=b'Vapour phase mol fraction'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eosflash',
            name='beta_vol',
            field=models.FloatField(null=True, verbose_name=b'Vapour phase volume fraction'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimentalflash',
            name='beta_mol',
            field=models.FloatField(null=True, verbose_name=b'Vapour phase mol fraction'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimentalflash',
            name='beta_vol',
            field=models.FloatField(null=True, verbose_name=b'Vapour phase volume fraction'),
            preserve_default=True,
        ),
    ]
