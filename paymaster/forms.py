# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from . import settings

class DefaultPaymentForm(forms.Form):
    amount = forms.DecimalField(
        label=_(u'Сумма'), min_value=settings.PAYMASTER_AMOUNT_MIN_VALUE,
        max_value=9999999, required=True)
