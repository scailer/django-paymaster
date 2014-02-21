# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Invoice


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'amount', 'payment_method',
                    'payment_id', 'payment_date', 'creation_date')
    search_fields = ['description']
    date_hierarchy = 'payment_date'

admin.site.register(Invoice, InvoiceAdmin)
