# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Compound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('formula', models.CharField(max_length=255)),
                ('formula_extended', models.TextField(null=True, blank=True)),
                ('tc', models.FloatField(verbose_name=b'Critical Temperature')),
                ('tc_unit', models.CharField(default=b'K', max_length=255, choices=[(b'degC', '\xb0C'), (b'K', b'K'), (b'degF', '\xb0F')])),
                ('pc', models.FloatField(verbose_name=b'Critical Pressure')),
                ('pc_unit', models.CharField(default=b'bar', max_length=255, choices=[(b'bar', b'bar'), (b'mmHg', b'mmHg'), (b'atm', b'atm'), (b'Pa', b'Pa'), (b'Pa', b'psi')])),
                ('vc', models.FloatField(verbose_name=b'Critical Volume')),
                ('vc_unit', models.CharField(default=b'L/mol', max_length=255, choices=[(b'L/mol', b'L/mol'), (b'mol/L', b'mol/L'), (b'g/cm**3', b'g/cm3')])),
                ('acentric_factor', models.FloatField(null=True, blank=True)),
                ('a', models.FloatField(null=True, blank=True)),
                ('b', models.FloatField(null=True, blank=True)),
                ('c', models.FloatField(null=True, blank=True)),
                ('d', models.FloatField(null=True, blank=True)),
                ('delta1', models.FloatField(null=True, blank=True)),
                ('weight', models.FloatField(null=True, editable=False, blank=True)),
            ],
            options={
                'ordering': ('mixturefraction__position', 'weight'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EosEnvelope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('p', picklefield.fields.PickledObjectField(help_text='Presure array of the envelope P-T', editable=False)),
                ('t', picklefield.fields.PickledObjectField(help_text='Temperature array of the envelope P-T', editable=False)),
                ('rho', picklefield.fields.PickledObjectField(help_text='Density array of the envelope P-T', null=True, editable=False)),
                ('p_cri', picklefield.fields.PickledObjectField(help_text='Presure coordenates of critical points', null=True, editable=False)),
                ('t_cri', picklefield.fields.PickledObjectField(help_text='Temperature coordenates of critical points', null=True, editable=False)),
                ('rho_cri', picklefield.fields.PickledObjectField(help_text='Density coordenates of critical points', null=True, editable=False)),
                ('index_cri', picklefield.fields.PickledObjectField(null=True, editable=False)),
                ('label', models.CharField(default=b'__nolengend__', max_length=100, null=True, blank=True)),
                ('input_txt', models.TextField(null=True, editable=False)),
                ('output_txt', models.TextField(null=True, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EosFlash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('t', models.FloatField(verbose_name=b'Temperature of the flash')),
                ('p', models.FloatField(verbose_name=b'Pressure of the flash')),
                ('rho_l', models.FloatField(null=True, verbose_name=b'Density of liquid')),
                ('rho_v', models.FloatField(null=True, verbose_name=b'Density of vapour')),
                ('beta', models.FloatField(null=True, verbose_name=b'Vapour fraction')),
                ('input_txt', models.TextField(null=True, editable=False)),
                ('output_txt', models.TextField(null=True, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EosSetup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='A short indentification for this EOS configuration', max_length=255, null=True, blank=True)),
                ('eos', models.CharField(default=b'RKPR', max_length=255, choices=[(b'SRK', b'SRK'), (b'PR', b'PR'), (b'RKPR', b'RKPR')])),
                ('kij_mode', models.CharField(default=b'constants', max_length=255, choices=[(b't_dep', b'Kij is temperature dependent'), (b'constants', b'kij is a constant for each binary interaction')])),
                ('lij_mode', models.CharField(default=b'zero', max_length=255, choices=[(b'zero', b'Lij is zero for each binary interaction'), (b'constants', b'Lij is a constant of each binary interaction')])),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExperimentalEnvelope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('p', picklefield.fields.PickledObjectField(help_text='Presure array of the envelope P-T', editable=False)),
                ('t', picklefield.fields.PickledObjectField(help_text='Temperature array of the envelope P-T', editable=False)),
                ('rho', picklefield.fields.PickledObjectField(help_text='Density array of the envelope P-T', null=True, editable=False)),
                ('p_cri', picklefield.fields.PickledObjectField(help_text='Presure coordenates of critical points', null=True, editable=False)),
                ('t_cri', picklefield.fields.PickledObjectField(help_text='Temperature coordenates of critical points', null=True, editable=False)),
                ('rho_cri', picklefield.fields.PickledObjectField(help_text='Density coordenates of critical points', null=True, editable=False)),
                ('index_cri', picklefield.fields.PickledObjectField(null=True, editable=False)),
                ('label', models.CharField(default=b'__nolengend__', max_length=100, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExperimentalFlash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('t', models.FloatField(verbose_name=b'Temperature of the flash')),
                ('p', models.FloatField(verbose_name=b'Pressure of the flash')),
                ('rho_l', models.FloatField(null=True, verbose_name=b'Density of liquid')),
                ('rho_v', models.FloatField(null=True, verbose_name=b'Density of vapour')),
                ('beta', models.FloatField(null=True, verbose_name=b'Vapour fraction')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='K0InteractionParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eos', models.CharField(max_length=255, choices=[(b'SRK', b'SRK'), (b'PR', b'PR'), (b'RKPR', b'RKPR')])),
                ('value', models.FloatField()),
                ('compounds', models.ManyToManyField(to='sur.Compound')),
                ('setup', models.ForeignKey(to='sur.EosSetup', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-setup', '-user'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KijInteractionParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eos', models.CharField(max_length=255, choices=[(b'SRK', b'SRK'), (b'PR', b'PR'), (b'RKPR', b'RKPR')])),
                ('value', models.FloatField()),
                ('compounds', models.ManyToManyField(to='sur.Compound')),
                ('setup', models.ForeignKey(to='sur.EosSetup', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-setup', '-user'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LijInteractionParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eos', models.CharField(max_length=255, choices=[(b'SRK', b'SRK'), (b'PR', b'PR'), (b'RKPR', b'RKPR')])),
                ('value', models.FloatField()),
                ('compounds', models.ManyToManyField(to='sur.Compound')),
                ('setup', models.ForeignKey(to='sur.EosSetup', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-setup', '-user'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Mixture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='A short indentification for this fluid/case', max_length=255, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MixtureFraction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fraction', models.DecimalField(max_digits=15, decimal_places=6)),
                ('position', models.PositiveIntegerField(editable=False)),
                ('compound', models.ForeignKey(to='sur.Compound')),
                ('mixture', models.ForeignKey(related_name='fractions', to='sur.Mixture')),
            ],
            options={
                'ordering': ('position',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TstarInteractionParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eos', models.CharField(max_length=255, choices=[(b'SRK', b'SRK'), (b'PR', b'PR'), (b'RKPR', b'RKPR')])),
                ('value', models.FloatField()),
                ('compounds', models.ManyToManyField(to='sur.Compound')),
                ('setup', models.ForeignKey(to='sur.EosSetup', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-setup', '-user'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mixturefraction',
            unique_together=set([('mixture', 'compound')]),
        ),
        migrations.AddField(
            model_name='mixture',
            name='Compounds',
            field=models.ManyToManyField(to='sur.Compound', through='sur.MixtureFraction'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mixture',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimentalflash',
            name='liquid_mixture',
            field=models.ForeignKey(related_name='experimental_flashes_as_liquid', to='sur.Mixture', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimentalflash',
            name='mixture',
            field=models.ForeignKey(related_name='experimentalflashes', to='sur.Mixture'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimentalflash',
            name='vapour_mixture',
            field=models.ForeignKey(related_name='experimental_flashes_as_gas', to='sur.Mixture', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experimentalenvelope',
            name='mixture',
            field=models.ForeignKey(related_name='experimentalenvelopes', to='sur.Mixture'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eosflash',
            name='liquid_mixture',
            field=models.ForeignKey(related_name='eos_flashes_as_liquid', to='sur.Mixture', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eosflash',
            name='mixture',
            field=models.ForeignKey(related_name='eosflashes', to='sur.Mixture'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eosflash',
            name='setup',
            field=models.ForeignKey(to='sur.EosSetup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eosflash',
            name='vapour_mixture',
            field=models.ForeignKey(related_name='eos_flashes_as_gas', to='sur.Mixture', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eosenvelope',
            name='mixture',
            field=models.ForeignKey(related_name='eosenvelopes', to='sur.Mixture'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eosenvelope',
            name='setup',
            field=models.ForeignKey(to='sur.EosSetup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alias',
            name='compound',
            field=models.ForeignKey(related_name='aliases', to='sur.Compound'),
            preserve_default=True,
        ),
    ]
