# -*- coding: utf-8 -*-

import base64
import urllib
import hashlib

from uuid import uuid4
from datetime import datetime, timedelta
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from django.utils.translation import ugettext_lazy as _

from .models import Invoice
from . import settings
from . import signals
from . import logger


class InitialView(generic.FormView):
    _payment_no = None

    phone_field = 'phone'
    email_field = 'email'
    amount_key = 'amount'

    def form_valid(self, form):
        if not self.request.user.is_authenticated():
            logger.warn(u'No user. Permission denied.')
            return HttpResponse('NO ACCESS', status=403)

        url = '{0}?{1}'.format(
            settings.PAYMASTER_INIT_URL,
            self.init_query(form)
        )

        logger.info(u'User {0} redirected to {1}'.format(
            self.request.user.username, url))

        return HttpResponseRedirect(url)

    def get_payer(self):
        return self.request.user

    def get_amount(self, form):
        return form.data.get(self.amount_key)

    def get_paymant_no(self, form):
        if not self._payment_no:
            number = None

            def _gen():
                _mask = '%Y%m%d-{0:08x}'.format(uuid4().get_fields()[0])
                return datetime.now().strftime(_mask)

            number = _gen()

            while Invoice.objects.filter(pk=number).exists():
                number = _gen()

            self._payment_no = number

        return self._payment_no

    def get_description(self, form):
        return _(settings.PAYMASTER_DESCRIPTION_MASK).format(
            payer=self.get_payer(),
            number=self.get_paymant_no(form)
        )

    def get_description_base64(self, form):
        return base64.encodestring(self.get_description(form).encode('utf-8'))

    def get_payer_phone(self, form):
        payer = self.get_payer()
        phone = getattr(payer, self.phone_field, None)

        if phone:
            return u''.join([x for x in phone if x in '1234567890'])

    def get_payer_email(self, form):
        payer = self.get_payer()
        return getattr(payer, self.email_field, None)

    def get_expires(self, form):
        return (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT%H:%M:%S")

    def get_payment_method(self, form):
        return settings.PAYMASTER_DEFAULT_PAYMENT_METHOD

    def get_extra_params(self, form):
        _d = isinstance(form.data, QueryDict) and form.data.dict() or form.data
        return _d

    def init_query(self, form):
        data = {
            'LMI_MERCHANT_ID': settings.PAYMASTER_MERCHANT_ID,
            'LMI_SHOP_ID': settings.PAYMASTER_SHOP_ID,
            'LMI_CURRENCY': settings.PAYMASTER_MERCHANT_CURRENCY,

            'LMI_PAYMENT_AMOUNT': self.get_amount(form),
            'LMI_PAYMENT_NO': self.get_paymant_no(form),
            'LMI_PAYMENT_DESC_BASE64': self.get_description_base64(form),
            'LMI_PAYER_PHONE_NUMBER': self.get_payer_phone(form),
            'LMI_PAYER_EMAIL': self.get_payer_email(form),
            'LMI_EXPIRES': self.get_expires(form),
            'LMI_PAYMENT_METHOD': self.get_payment_method(form),

            'LMI_SIM_MODE': settings.PAYMASTER_SIM_MODE,
            'LMI_SUCCESS_URL': settings.PAYMASTER_SUCCESS_URL,
            'LMI_FAILURE_URL': settings.PAYMASTER_FAILURE_URL,
            'LMI_INVOICE_CONFIRMATION_URL': (
                settings.PAYMASTER_INVOICE_CONFIRMATION_URL),
            'LMI_PAYMENT_NOTIFICATION_URL': (
                settings.PAYMASTER_PAYMENT_NOTIFICATION_URL),
        }

        data.update(self.get_extra_params(form))

        signals.invoice_init.send(sender=self, data=data)

        data = {k: v for k, v in data.items() if v}
        return urllib.urlencode(data)


class ConfirmView(generic.View):
    def post(self, request):
        invoice = Invoice.objects.create_from_api(request.POST)
        logger.info(u'Invoice {0} payment confirm.'.format(invoice.number))
        signals.invoice_confirm.send(sender=self, invoice=invoice)
        return HttpResponse('YES', content_type='text/plain')


class NotificationView(generic.View):
    _hash_fields = settings.PAYMASTER_HASH_FIELDS

    def check_hash(self, data):
        _line = u';'.join([data.get(key) for key in self._hash_fields])
        _line += u';{0}'.format(settings.PAYMASTER_PASSWORD)

        hash_method = settings.PAYMASTER_HASH_METHOD
        _hash = getattr(hashlib, hash_method)(_line.encode('utf-8'))
        return _hash.hexdigest() == data.get('LMI_HASH')

    def post(self, request):
        if not self.check_hash(request.POST):
            logger.error(
                u'Invoice {0} payment failed by reason: HashError'.format(
                    request.POST.get('LMI_PAYMENT_NO')))
            return HttpResponse('HashError')

        try:
            invoice = Invoice.objects.finalize(request.POST)
        except Invoice.InvoiceDuplication:
            logger.error(
                u'Invoice {0} payment failed by reason: Duplication'.format(
                    request.POST.get('LMI_PAYMENT_NO')))

            return HttpResponse('InvoiceDuplicationError')

        logger.info(u'Invoice {0} paid succesfully.'.format(invoice.number))

        signals.invoice_paid.send(sender=self, invoice=invoice)
        return HttpResponse('')


class SuccessView(generic.TemplateView):
    def get(self, request):
        invoice = Invoice.objects.get(pk=request.REQUEST['LMI_PAYMENT_NO'])
        logger.info(u'Invoice {0} success page visited'.format(invoice.number))
        signals.success_visited.send(sender=self, invoice=invoice)
        return super(SuccessView, self).get(request)

    def post(self, request):
        return self.get(request)


class FailView(generic.TemplateView):
    def get(self, request):
        invoice = Invoice.objects.get(pk=request.REQUEST['LMI_PAYMENT_NO'])
        logger.info(u'Invoice {0} fail page visited'.format(invoice.number))
        signals.fail_visited.send(sender=self, invoice=invoice)
        return super(FailView, self).get(request)

    def post(self, request):
        return self.get(request)
