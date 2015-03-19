# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sur', '0004_auto_20150210_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eosflash',
            name='beta_mol',
            field=models.FloatField(null=True, verbose_name=b'Vapour phase mol fraction', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eosflash',
            name='beta_vol',
            field=models.FloatField(null=True, verbose_name=b'Vapour phase volume fraction', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eosflash',
            name='p',
            field=models.FloatField(null=True, verbose_name=b'Pressure of the flash', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eosflash',
            name='rho_l',
            field=models.FloatField(null=True, verbose_name=b'Density of liquid', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eosflash',
            name='rho_v',
            field=models.FloatField(null=True, verbose_name=b'Density of vapour', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='eosflash',
            name='v',
            field=models.FloatField(null=True, verbose_name=b'Volume of the flash', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experimentalflash',
            name='beta_mol',
            field=models.FloatField(null=True, verbose_name=b'Vapour phase mol fraction', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experimentalflash',
            name='beta_vol',
            field=models.FloatField(null=True, verbose_name=b'Vapour phase volume fraction', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experimentalflash',
            name='p',
            field=models.FloatField(null=True, verbose_name=b'Pressure of the flash', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experimentalflash',
            name='rho_l',
            field=models.FloatField(null=True, verbose_name=b'Density of liquid', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experimentalflash',
            name='rho_v',
            field=models.FloatField(null=True, verbose_name=b'Density of vapour', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experimentalflash',
            name='v',
            field=models.FloatField(null=True, verbose_name=b'Volume of the flash', blank=True),
            preserve_default=True,
        ),
    ]
