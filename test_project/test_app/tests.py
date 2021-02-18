# -*- coding: utf-8 -*-

import base64
import hashlib

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import QueryDict

from paymaster import settings, utils
from paymaster.models import Invoice
from .models import ActivityLog


class TestAll(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(
            username='user', password='pass')

    def testAll(self):
        assert ActivityLog.objects.count() == 0

        url = reverse('paymaster:init')
        response = self.client.post(url, {})
        assert 200 == response.status_code

        response = self.client.post(url, {'amount': 11})
        assert 403 == response.status_code

        self.client.login(username='user', password='pass')

        response = self.client.post(url, {'amount': 1})
        assert 200 == response.status_code
        assert ActivityLog.objects.count() == 0

        response = self.client.post(url, {'amount': 13})
        assert 200 == response.status_code
        assert ActivityLog.objects.count() == 0

        response = self.client.post(url, {'amount': 11})
        assert 302 == response.status_code
        assert ActivityLog.objects.filter(action='init').count() == 1

        data = QueryDict(response.get('Location').split('?')[-1]).dict()
        data['LMI_PAYMENT_DESC'] = base64.b64decode(data['LMI_PAYMENT_DESC_BASE64'])
        data['LMI_PAID_AMOUNT'] = data['LMI_PAYMENT_AMOUNT']
        data['LMI_PAID_CURRENCY'] = data['LMI_CURRENCY']
        data['LMI_PAYMENT_SYSTEM'] = 'WebMoney'
        data['LMI_SIM_MODE'] = ''

        self.client = Client()
        response = self.client.post(reverse('paymaster:confirm'), data)
        assert 200 == response.status_code
        assert response.content == b'YES'
        assert ActivityLog.objects.filter(action='confirm').count() == 1

        data['LMI_SYS_PAYMENT_ID'] = 'A184F-CA23'
        data['LMI_SYS_PAYMENT_DATE'] = '2014-01-12T11:11:11'

        _line = u';'.join([data.get(key) for key in settings.PAYMASTER_HASH_FIELDS])
        _line += u';{0}'.format(settings.PAYMASTER_PASSWORD)

        hash_method = settings.PAYMASTER_HASH_METHOD
        _hash = getattr(hashlib, hash_method)(_line.encode('utf-8'))
        _hash = base64.b64encode(_hash.digest())

        response = self.client.post(reverse('paymaster:paid'), data)
        assert 200 == response.status_code
        assert b'HashError' in response.content
        assert ActivityLog.objects.filter(action='paid').count() == 0

        response = self.client.post(reverse('paymaster:fail'), data)
        assert 200 == response.status_code
        assert ActivityLog.objects.filter(action='fail').count() == 1

        data['LMI_HASH'] = _hash.decode()

        response = self.client.post(reverse('paymaster:paid'), data)
        assert 200 == response.status_code
        assert ActivityLog.objects.filter(action='paid').count() == 1
        assert Invoice.objects.get().is_paid()

        response = self.client.post(reverse('paymaster:paid'), data)
        assert 200 == response.status_code
        assert b'InvoiceDuplicationError' in response.content
        assert ActivityLog.objects.filter(action='paid').count() == 1

        response = self.client.post(reverse('paymaster:success'), data)
        assert 200 == response.status_code
        assert ActivityLog.objects.filter(action='success').count() == 1

        data['LMI_PAYMENT_NO'] = '12345678-12345678'
        response = self.client.post(reverse('paymaster:fail'), data)
        assert 200 == response.status_code

    def testElse(self):
        user = get_user_model().objects.all()[0]
        enc = utils.encode_payer(user)
        utils.decode_payer(enc + '111')

        user.pk = 1111
        enc = utils.encode_payer(user)
        utils.decode_payer(enc)

        assert True
