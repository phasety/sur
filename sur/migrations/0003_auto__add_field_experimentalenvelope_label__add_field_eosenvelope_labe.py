# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ExperimentalEnvelope.label'
        db.add_column(u'sur_experimentalenvelope', 'label',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'EosEnvelope.label'
        db.add_column(u'sur_eosenvelope', 'label',
                      self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ExperimentalEnvelope.label'
        db.delete_column(u'sur_experimentalenvelope', 'label')

        # Deleting field 'EosEnvelope.label'
        db.delete_column(u'sur_eosenvelope', 'label')


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
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'eosenvelopes'", 'to': u"orm['sur.Mixture']"}),
            'output_txt': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'p': ('picklefield.fields.PickledObjectField', [], {}),
            'p_cri': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'rho': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
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
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'mixture': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'experimentalenvelopes'", 'to': u"orm['sur.Mixture']"}),
            'p': ('picklefield.fields.PickledObjectField', [], {}),
            'p_cri': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
            'rho': ('picklefield.fields.PickledObjectField', [], {'null': 'True'}),
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