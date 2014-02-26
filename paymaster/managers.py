# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models


API_MAP = {
    'LMI_PAYMENT_NO': 'number',
    'LMI_PAYMENT_DESC': 'description',
    'LMI_PAYMENT_AMOUNT': 'amount',
    'LMI_CURRENCY': 'currency',
    'LMI_PAID_AMOUNT': 'paid_amount',
    'LMI_PAID_CURRENCY': 'paid_currency',
    'LMI_PAYMENT_SYSTEM': 'payment_system',
    'LMI_PAYMENT_METHOD': 'payment_method',

    'LMI_SYS_PAYMENT_ID': 'payment_id',
    'LMI_SYS_PAYMENT_DATE': 'payment_date',
    'LMI_PAYER_IDENTIFIER': 'payer_id',
}


class InvoiceDuplication(Exception):
    pass


class InvoiceManager(models.Manager):
    def create_from_api(self, data):
        _d = {mkey: data.get(akey) for akey, mkey in API_MAP.items()}
        return self.create(**_d)

    def finalize(self, data):
        invoice = self.get(number=data['LMI_PAYMENT_NO'])

        if invoice.payment_id:
            raise InvoiceDuplication()

        date = data['LMI_SYS_PAYMENT_DATE']
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        data = hasattr(data, 'dict') and data.dict() or data
        data['LMI_SYS_PAYMENT_DATE'] = date

        for akey, mkey in API_MAP.items():
            setattr(invoice, mkey, data.get(akey))

        invoice.save()
        return invoice
