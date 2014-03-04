# -*- coding: utf-8 -*-

import logging
from django.conf import settings as user_settings
from django.core.exceptions import ImproperlyConfigured

LOCAL = {
    'PAYMASTER_INIT_URL': 'https://paymaster.ru/Payment/Init',

    'PAYMASTER_LOGIN': None,
    'PAYMASTER_PASSWORD': None,
    'PAYMASTER_MERCHANT_ID': None,
    'PAYMASTER_SHOP_ID': None,
    'PAYMASTER_HASH_METHOD': 'md5',

    'PAYMASTER_MERCHANT_CURRENCY': u'RUB',
    'PAYMASTER_DEFAULT_PAYMENT_METHOD': u'WebMoney',
    'PAYMASTER_DESCRIPTION_MASK': (
        u'Пополнение баланса для пользователя {payer.email} [{number}]'),
    'PAYMASTER_INVOICE_NUMBER_GENERATOR': None,

    'PAYMASTER_SIM_MODE': None,
    'PAYMASTER_INVOICE_CONFIRMATION_URL': None,
    'PAYMASTER_PAYMENT_NOTIFICATION_URL': None,
    'PAYMASTER_SUCCESS_URL': None,
    'PAYMASTER_FAILURE_URL': None,

    'PAYMASTER_USER_PHONE_FIELD': None,
    'PAYMASTER_USER_EMAIL_FIELD': None,

    'PAYMASTER_HASH_FIELDS': (
        'LMI_MERCHANT_ID', 'LMI_PAYMENT_NO', 'LMI_SYS_PAYMENT_ID',
        'LMI_SYS_PAYMENT_DATE', 'LMI_PAYMENT_AMOUNT', 'LMI_CURRENCY',
        'LMI_PAID_AMOUNT', 'LMI_PAID_CURRENCY', 'LMI_PAYMENT_SYSTEM',
        'LMI_SIM_MODE'
    ),
}

REQUIRED = ['PAYMASTER_PASSWORD', 'PAYMASTER_MERCHANT_ID']


class LocalSettings(object):
    def __init__(self, local_settings, outer_settings):
        self.local_settings = local_settings
        self.outer_settings = outer_settings

        values = [getattr(outer_settings, name, None) for name in REQUIRED]
        if not all(values):
            raise ImproperlyConfigured(
                'The {0} setting must not be empty. Pleaze, set it or disable '
                'paymaster application.'.format(', '.join(REQUIRED)))

    def __getattr__(self, name):
        return getattr(self.outer_settings, name,
                       self.local_settings.get(name))

settings = LocalSettings(LOCAL, user_settings)
logger = logging.getLogger('paymaster')
