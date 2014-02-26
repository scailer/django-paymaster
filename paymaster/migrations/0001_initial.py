# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Invoice'
        db.create_table(u'paymaster_invoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=17)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=11, decimal_places=2)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('paid_amount', self.gf('django.db.models.fields.DecimalField')(max_digits=11, decimal_places=2)),
            ('paid_currency', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('payment_method', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('payment_system', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('payment_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('payer_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('payment_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('edition_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'paymaster', ['Invoice'])


    def backwards(self, orm):
        # Deleting model 'Invoice'
        db.delete_table(u'paymaster_invoice')


    models = {
        u'paymaster.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'edition_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '17'}),
            'paid_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'paid_currency': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'payer_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'payment_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'payment_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_system': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['paymaster']