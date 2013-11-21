# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Compound'
        db.create_table(u'sur_compound', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('formula', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('formula_extended', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('tc', self.gf('django.db.models.fields.FloatField')()),
            ('tc_unit', self.gf('django.db.models.fields.CharField')(default='K', max_length=255)),
            ('pc', self.gf('django.db.models.fields.FloatField')()),
            ('pc_unit', self.gf('django.db.models.fields.CharField')(default='bar', max_length=255)),
            ('vc', self.gf('django.db.models.fields.FloatField')()),
            ('vc_unit', self.gf('django.db.models.fields.CharField')(default='L/mol', max_length=255)),
            ('acentric_factor', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('a', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('b', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('c', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('d', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('delta1', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'sur', ['Compound'])

        # Adding model 'Alias'
        db.create_table(u'sur_alias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('compound', self.gf('django.db.models.fields.related.ForeignKey')(related_name='aliases', to=orm['sur.Compound'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'sur', ['Alias'])

        # Adding model 'EosSetup'
        db.create_table(u'sur_eossetup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('eos', self.gf('django.db.models.fields.CharField')(default='RKPR', max_length=255)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('kij_mode', self.gf('django.db.models.fields.CharField')(default='constants', max_length=255)),
            ('lij_mode', self.gf('django.db.models.fields.CharField')(default='zero', max_length=255)),
        ))
        db.send_create_signal(u'sur', ['EosSetup'])

        # Adding model 'KijInteractionParameter'
        db.create_table(u'sur_kijinteractionparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('eos', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('setup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sur.EosSetup'], null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal(u'sur', ['KijInteractionParameter'])

        # Adding M2M table for field compounds on 'KijInteractionParameter'
        m2m_table_name = db.shorten_name(u'sur_kijinteractionparameter_compounds')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('kijinteractionparameter', models.ForeignKey(orm[u'sur.kijinteractionparameter'], null=False)),
            ('compound', models.ForeignKey(orm[u'sur.compound'], null=False))
        ))
        db.create_unique(m2m_table_name, ['kijinteractionparameter_id', 'compound_id'])

        # Adding model 'K0InteractionParameter'
        db.create_table(u'sur_k0interactionparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('eos', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('setup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sur.EosSetup'], null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal(u'sur', ['K0InteractionParameter'])

        # Adding M2M table for field compounds on 'K0InteractionParameter'
        m2m_table_name = db.shorten_name(u'sur_k0interactionparameter_compounds')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('k0interactionparameter', models.ForeignKey(orm[u'sur.k0interactionparameter'], null=False)),
            ('compound', models.ForeignKey(orm[u'sur.compound'], null=False))
        ))
        db.create_unique(m2m_table_name, ['k0interactionparameter_id', 'compound_id'])

        # Adding model 'TstarInteractionParameter'
        db.create_table(u'sur_tstarinteractionparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('eos', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('setup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sur.EosSetup'], null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal(u'sur', ['TstarInteractionParameter'])

        # Adding M2M table for field compounds on 'TstarInteractionParameter'
        m2m_table_name = db.shorten_name(u'sur_tstarinteractionparameter_compounds')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tstarinteractionparameter', models.ForeignKey(orm[u'sur.tstarinteractionparameter'], null=False)),
            ('compound', models.ForeignKey(orm[u'sur.compound'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tstarinteractionparameter_id', 'compound_id'])

        # Adding model 'LijInteractionParameter'
        db.create_table(u'sur_lijinteractionparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('eos', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('setup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sur.EosSetup'], null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal(u'sur', ['LijInteractionParameter'])

        # Adding M2M table for field compounds on 'LijInteractionParameter'
        m2m_table_name = db.shorten_name(u'sur_lijinteractionparameter_compounds')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('lijinteractionparameter', models.ForeignKey(orm[u'sur.lijinteractionparameter'], null=False)),
            ('compound', models.ForeignKey(orm[u'sur.compound'], null=False))
        ))
        db.create_unique(m2m_table_name, ['lijinteractionparameter_id', 'compound_id'])

        # Adding model 'MixtureFraction'
        db.create_table(u'sur_mixturefraction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mixture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fractions', to=orm['sur.Mixture'])),
            ('compound', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sur.Compound'])),
            ('fraction', self.gf('django.db.models.fields.DecimalField')(max_digits=15, decimal_places=4)),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'sur', ['MixtureFraction'])

        # Adding unique constraint on 'MixtureFraction', fields ['mixture', 'compound']
        db.create_unique(u'sur_mixturefraction', ['mixture_id', 'compound_id'])

        # Adding model 'Mixture'
        db.create_table(u'sur_mixture', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
        ))
        db.send_create_signal(u'sur', ['Mixture'])

        # Adding model 'ExperimentalEnvelope'
        db.create_table(u'sur_experimentalenvelope', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mixture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='experimentalenvelopes', to=orm['sur.Mixture'])),
            ('p', self.gf('picklefield.fields.PickledObjectField')()),
            ('t', self.gf('picklefield.fields.PickledObjectField')()),
            ('rho', self.gf('picklefield.fields.PickledObjectField')()),
            ('p_cri', self.gf('picklefield.fields.PickledObjectField')(null=True)),
            ('t_cri', self.gf('picklefield.fields.PickledObjectField')(null=True)),
            ('rho_cri', self.gf('picklefield.fields.PickledObjectField')(null=True)),
            ('index_cri', self.gf('picklefield.fields.PickledObjectField')(null=True)),
        ))
        db.send_create_signal(u'sur', ['ExperimentalEnvelope'])

        # Adding model 'EosEnvelope'
        db.create_table(u'sur_eosenvelope', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mixture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='eosenvelopes', to=orm['sur.Mixture'])),
            ('p', self.gf('picklefield.fields.PickledObjectField')()),
            ('t', self.gf('picklefield.fields.PickledObjectField')()),
            ('rho', self.gf('picklefield.fields.PickledObjectField')()),
            ('p_cri', self.gf('picklefield.fields.PickledObjectField')(null=True)),
            ('t_cri', self.gf('picklefield.fields.PickledObjectField')(null=True)),
            ('rho_cri', self.gf('picklefield.fields.PickledObjectField')(null=True)),
            ('index_cri', self.gf('picklefield.fields.PickledObjectField')(null=True)),
            ('setup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sur.EosSetup'])),
            ('input_txt', self.gf('django.db.models.fields.TextField')(null=True)),
            ('output_txt', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal(u'sur', ['EosEnvelope'])

        # Adding model 'ExperimentalFlash'
        db.create_table(u'sur_experimentalflash', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mixture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='experimentalflashes', to=orm['sur.Mixture'])),
            ('t', self.gf('django.db.models.fields.FloatField')()),
            ('p', self.gf('django.db.models.fields.FloatField')()),
            ('rho_l', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('rho_v', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('beta', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('vapour_mixture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='experimental_flashes_as_gas', null=True, to=orm['sur.Mixture'])),
            ('liquid_mixture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='experimental_flashes_as_liquid', null=True, to=orm['sur.Mixture'])),
        ))
        db.send_create_signal(u'sur', ['ExperimentalFlash'])

        # Adding model 'EosFlash'
        db.create_table(u'sur_eosflash', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mixture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='eosflashes', to=orm['sur.Mixture'])),
            ('t', self.gf('django.db.models.fields.FloatField')()),
            ('p', self.gf('django.db.models.fields.FloatField')()),
            ('rho_l', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('rho_v', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('beta', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('setup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sur.EosSetup'])),
            ('vapour_mixture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='eos_flashes_as_gas', null=True, to=orm['sur.Mixture'])),
            ('liquid_mixture', self.gf('django.db.models.fields.related.ForeignKey')(related_name='eos_flashes_as_liquid', null=True, to=orm['sur.Mixture'])),
        ))
        db.send_create_signal(u'sur', ['EosFlash'])


    def backwards(self, orm):
        # Removing unique constraint on 'MixtureFraction', fields ['mixture', 'compound']
        db.delete_unique(u'sur_mixturefraction', ['mixture_id', 'compound_id'])

        # Deleting model 'Compound'
        db.delete_table(u'sur_compound')

        # Deleting model 'Alias'
        db.delete_table(u'sur_alias')

        # Deleting model 'EosSetup'
        db.delete_table(u'sur_eossetup')

        # Deleting model 'KijInteractionParameter'
        db.delete_table(u'sur_kijinteractionparameter')

        # Removing M2M table for field compounds on 'KijInteractionParameter'
        db.delete_table(db.shorten_name(u'sur_kijinteractionparameter_compounds'))

        # Deleting model 'K0InteractionParameter'
        db.delete_table(u'sur_k0interactionparameter')

        # Removing M2M table for field compounds on 'K0InteractionParameter'
        db.delete_table(db.shorten_name(u'sur_k0interactionparameter_compounds'))

        # Deleting model 'TstarInteractionParameter'
        db.delete_table(u'sur_tstarinteractionparameter')

        # Removing M2M table for field compounds on 'TstarInteractionParameter'
        db.delete_table(db.shorten_name(u'sur_tstarinteractionparameter_compounds'))

        # Deleting model 'LijInteractionParameter'
        db.delete_table(u'sur_lijinteractionparameter')

        # Removing M2M table for field compounds on 'LijInteractionParameter'
        db.delete_table(db.shorten_name(u'sur_lijinteractionparameter_compounds'))

        # Deleting model 'MixtureFraction'
        db.delete_table(u'sur_mixturefraction')

        # Deleting model 'Mixture'
        db.delete_table(u'sur_mixture')

        # Deleting model 'ExperimentalEnvelope'
        db.delete_table(u'sur_experimentalenvelope')

        # Deleting model 'EosEnvelope'
        db.delete_table(u'sur_eosenvelope')

        # Deleting model 'ExperimentalFlash'
        db.delete_table(u'sur_experimentalflash')

        # Deleting model 'EosFlash'
        db.delete_table(u'sur_eosflash')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'sur.alias': {
            'Meta': {'object_name': 'Alias'},
            'compound': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aliases'", 'to': u"orm['sur.Compound']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'sur.compound': {
            'Meta': {'ordering': "('mixturefraction__position', 'weight')", 'object_name': 'Compound'},
            'a': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'acentric_factor': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'b': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'c': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'd': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'delta1': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'formula': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'formula_extended': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'pc': ('django.db.models.fields.FloatField', [], {}),
            'pc_unit': ('django.db.models.fields.CharField', [], {'default': "'bar'", 'max_length': '255'}),
            'tc': ('django.db.models.fields.FloatField', [], {}),
            'tc_unit': ('django.db.models.fields.CharField', [], {'default': "'K'", 'max_length': '255'}),
            'vc': ('django.db.models.fields.FloatField', [], {}),
            'vc_unit': ('django.db.models.fields.CharField', [], {'default': "'L/mol'", 'max_length': '255'}),
            'weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'sur.eosenvelope': {
            'Meta': {'object_name': 'EosEnvelope'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_cri': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'input_txt': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'eosenvelopes'", 'to': u"orm['sur.Mixture']"}),
            'output_txt': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'p': ('picklefield.fields.PickledObjectField', [], {}),
            'p_cri': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'rho': ('picklefield.fields.PickledObjectField', [], {}),
            'rho_cri': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'setup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sur.EosSetup']"}),
            't': ('picklefield.fields.PickledObjectField', [], {}),
            't_cri': ('picklefield.fields.PickledObjectField', [], {'null': 'True'})
        },
        u'sur.eosflash': {
            'Meta': {'object_name': 'EosFlash'},
            'beta': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'liquid_mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'eos_flashes_as_liquid'", 'null': 'True', 'to': u"orm['sur.Mixture']"}),
            'mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'eosflashes'", 'to': u"orm['sur.Mixture']"}),
            'p': ('django.db.models.fields.FloatField', [], {}),
            'rho_l': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rho_v': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'setup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sur.EosSetup']"}),
            't': ('django.db.models.fields.FloatField', [], {}),
            'vapour_mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'eos_flashes_as_gas'", 'null': 'True', 'to': u"orm['sur.Mixture']"})
        },
        u'sur.eossetup': {
            'Meta': {'object_name': 'EosSetup'},
            'eos': ('django.db.models.fields.CharField', [], {'default': "'RKPR'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kij_mode': ('django.db.models.fields.CharField', [], {'default': "'constants'", 'max_length': '255'}),
            'lij_mode': ('django.db.models.fields.CharField', [], {'default': "'zero'", 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'sur.experimentalenvelope': {
            'Meta': {'object_name': 'ExperimentalEnvelope'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_cri': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'experimentalenvelopes'", 'to': u"orm['sur.Mixture']"}),
            'p': ('picklefield.fields.PickledObjectField', [], {}),
            'p_cri': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'rho': ('picklefield.fields.PickledObjectField', [], {}),
            'rho_cri': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            't': ('picklefield.fields.PickledObjectField', [], {}),
            't_cri': ('picklefield.fields.PickledObjectField', [], {'null': 'True'})
        },
        u'sur.experimentalflash': {
            'Meta': {'object_name': 'ExperimentalFlash'},
            'beta': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'liquid_mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'experimental_flashes_as_liquid'", 'null': 'True', 'to': u"orm['sur.Mixture']"}),
            'mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'experimentalflashes'", 'to': u"orm['sur.Mixture']"}),
            'p': ('django.db.models.fields.FloatField', [], {}),
            'rho_l': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'rho_v': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            't': ('django.db.models.fields.FloatField', [], {}),
            'vapour_mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'experimental_flashes_as_gas'", 'null': 'True', 'to': u"orm['sur.Mixture']"})
        },
        u'sur.k0interactionparameter': {
            'Meta': {'ordering': "['-setup', '-user']", 'object_name': 'K0InteractionParameter'},
            'compounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sur.Compound']", 'symmetrical': 'False'}),
            'eos': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sur.EosSetup']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'sur.kijinteractionparameter': {
            'Meta': {'ordering': "['-setup', '-user']", 'object_name': 'KijInteractionParameter'},
            'compounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sur.Compound']", 'symmetrical': 'False'}),
            'eos': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sur.EosSetup']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'sur.lijinteractionparameter': {
            'Meta': {'ordering': "['-setup', '-user']", 'object_name': 'LijInteractionParameter'},
            'compounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sur.Compound']", 'symmetrical': 'False'}),
            'eos': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sur.EosSetup']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'sur.mixture': {
            'Compounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sur.Compound']", 'through': u"orm['sur.MixtureFraction']", 'symmetrical': 'False'}),
            'Meta': {'object_name': 'Mixture'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'sur.mixturefraction': {
            'Meta': {'ordering': "('position',)", 'unique_together': "(('mixture', 'compound'),)", 'object_name': 'MixtureFraction'},
            'compound': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sur.Compound']"}),
            'fraction': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '4'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fractions'", 'to': u"orm['sur.Mixture']"}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'sur.tstarinteractionparameter': {
            'Meta': {'ordering': "['-setup', '-user']", 'object_name': 'TstarInteractionParameter'},
            'compounds': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sur.Compound']", 'symmetrical': 'False'}),
            'eos': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sur.EosSetup']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['sur']