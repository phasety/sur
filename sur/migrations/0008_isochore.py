# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sur', '0007_auto_20150320_1419'),
    ]

    operations = [
        migrations.CreateModel(
            name='Isochore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('v', models.FloatField(verbose_name=b'Volume of the isochore')),
                ('ts', models.FloatField(verbose_name=b'Temperature')),
                ('ps', models.FloatField(verbose_name=b'Pressure')),
                ('t_sup', models.FloatField(verbose_name=b'Temperature sup')),
                ('t_step', models.FloatField(verbose_name=b'Temperature step')),
                ('t_inf', models.FloatField(verbose_name=b'Temperature inf')),
                ('p', picklefield.fields.PickledObjectField(help_text='Presure array of the envelope P-T', editable=False)),
                ('t', picklefield.fields.PickledObjectField(help_text='Temperature array of the envelope P-T', editable=False)),
                ('rho', picklefield.fields.PickledObjectField(help_text='Density array of the envelope P-T', null=True, editable=False)),
                ('beta_mol', picklefield.fields.PickledObjectField(help_text=b'Vapour phase mol fraction', null=True, editable=False)),
                ('beta_vol', picklefield.fields.PickledObjectField(help_text=b'Vapour phase vol fraction', null=True, editable=False)),
                ('p_monophasic', picklefield.fields.PickledObjectField(help_text='Presure array of the envelope P-T', editable=False)),
                ('t_monophasic', picklefield.fields.PickledObjectField(help_text='Temperature array of the envelope P-T', editable=False)),
                ('rho_monophasic', picklefield.fields.PickledObjectField(help_text='Density array of the envelope P-T', null=True, editable=False)),
                ('input_txt', models.TextField(null=True, editable=False)),
                ('output_txt', models.TextField(null=True, editable=False)),
                ('mixture', models.ForeignKey(related_name='isochorees', to='sur.Mixture')),
                ('setup', models.ForeignKey(to='sur.EosSetup')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
