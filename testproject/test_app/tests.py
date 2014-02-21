# -*- coding: utf-8 -*-

import base64
import hashlib

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.http import QueryDict

from paymaster import settings
from .models import ActivityLog


class TestAll(TestCase):
    def setUp(self):
        get_user_model().objects.create_user(
            username='user', password='pass')

    def testAll(self):
        assert ActivityLog.objects.count() == 0

        url = reverse('paymaster:init')
        response = self.client.post(url, {'amount': 11})
        assert 403 == response.status_code

        response = self.client.post(url, {'amount': 1})
        assert 200 == response.status_code
        assert ActivityLog.objects.count() == 0

        self.client.login(username='user', password='pass')
        response = self.client.post(url, {'amount': 11})
        assert 302 == response.status_code
        assert ActivityLog.objects.filter(action='init').count() == 1

        data = QueryDict(response.get('Location').split('?')[-1]).dict()
        data['LMI_PAYMENT_DESC'] = base64.decodestring(
            data['LMI_PAYMENT_DESC_BASE64'])
        data['LMI_PAID_AMOUNT'] = data['LMI_PAYMENT_AMOUNT']
        data['LMI_PAID_CURRENCY'] = data['LMI_CURRENCY']
        data['LMI_PAYMENT_SYSTEM'] = 'WebMoney'
        data['LMI_SIM_MODE'] = ''

        self.client = Client()
        response = self.client.post(reverse('paymaster:confirm'), data)
        assert 200 == response.status_code
        assert response.content == 'YES'
        assert ActivityLog.objects.filter(action='confirm').count() == 1

        data['LMI_SYS_PAYMENT_ID'] = 'A184F-CA23'
        data['LMI_SYS_PAYMENT_DATE'] = '2014-01-12T11:11:11'

        _line = u';'.join([data.get(key) for key in settings.HASH_FIELDS])
        _line += u';{0}'.format(settings.PAYMASTER_PASSWORD)

        hash_method = settings.PAYMASTER_HASH_METHOD
        _hash = getattr(hashlib, hash_method)(_line.encode('utf-8'))

        response = self.client.post(reverse('paymaster:paid'), data)
        assert 200 == response.status_code
        assert 'HashError' in response.content
        assert ActivityLog.objects.filter(action='paid').count() == 0

        response = self.client.post(reverse('paymaster:fail'), data)
        assert 200 == response.status_code
        assert ActivityLog.objects.filter(action='fail').count() == 1

        data['LMI_HASH'] = _hash.hexdigest()

        response = self.client.post(reverse('paymaster:paid'), data)
        assert 200 == response.status_code
        assert ActivityLog.objects.filter(action='paid').count() == 1

        response = self.client.post(reverse('paymaster:paid'), data)
        assert 200 == response.status_code
        assert 'InvoiceDuplicationError' in response.content
        assert ActivityLog.objects.filter(action='paid').count() == 1

        response = self.client.post(reverse('paymaster:success'), data)
        assert 200 == response.status_code
        assert ActivityLog.objects.filter(action='success').count() == 1
