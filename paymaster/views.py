# -*- coding: utf-8 -*-

"""
    Обработчики запросов для взаимодействия с API PayMaster
    https://paymaster.ru/Partners/ru/docs/protocol

    @author: Vlasov Dmitry
    @contact: scailer@russia.ru
    @status: stable
"""

import base64
import urllib
import hashlib
from datetime import datetime, timedelta

from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Invoice
from . import settings
from . import signals
from . import logger
from . import utils


class InitialView(generic.FormView):
    """
        Форма инициации платежа.

        Данный обработчик предназначен для формирования запроса инициации
        платежа. Здесь будут сформированы параметры платежа в соответствии
        с настройками приложения и имеющимися данными пользователя.
    """

    _payment_no = None

    phone_field = 'phone'
    email_field = 'email'
    amount_key = 'amount'

    def form_valid(self, form):
        """ Формируем переход на сайт платежной системы """
        if not self.request.user.is_authenticated():
            logger.warn(u'No user. Permission denied.')
            return HttpResponse('NO ACCESS', status=403)

        try:
            url = '{0}?{1}'.format(
                settings.PAYMASTER_INIT_URL,
                self.init_query(form))
        except ValidationError:
            return self.form_invalid(form)

        logger.info(u'User {0} redirected to {1}'.format(
            self.request.user.username, url))

        return HttpResponseRedirect(url)

    def get_payer(self):
        """ Получаем объект-плательщика """
        return self.request.user

    def get_payer_id(self):
        """ Получаем кодированный идентификатор плательщика """
        return utils.encode_payer(self.request.user)

    def get_amount(self, form):
        """ Получаем сумму платежа """
        return form.data.get(self.amount_key)

    def get_paymant_no(self, form):
        """ Генерируем номер платежа """
        _gen = (settings.PAYMASTER_INVOICE_NUMBER_GENERATOR
                or utils.number_generetor)

        if not self._payment_no:
            number = _gen(self, form)

            while Invoice.objects.filter(number=number).exists():
                number = _gen(self, form)

            self._payment_no = number

        return self._payment_no

    def get_description(self, form):
        """ Получаем описание """
        return _(settings.PAYMASTER_DESCRIPTION_MASK).format(
            payer=self.get_payer(),
            number=self.get_paymant_no(form)
        )

    def get_description_base64(self, form):
        """ Пререводим описание в base64 """
        return base64.encodestring(self.get_description(form).encode('utf-8'))

    def get_payer_phone(self, form):
        """ Получаем номер телефона в формате 79031234567 """
        payer = self.get_payer()
        phone = getattr(payer, self.phone_field, None)

        if phone is not None:
            return u''.join(x for x in unicode(phone) if x in '1234567890')

    def get_payer_email(self, form):
        """ Получаем электронную почту """
        payer = self.get_payer()
        return getattr(payer, self.email_field, None)

    def get_expires(self, form):
        """ Получаем дату истечения счета YYYY-MM-DDThh:mm:ss """
        return (datetime.now() + timedelta(1)).strftime("%Y-%m-%dT%H:%M:%S")

    def get_payment_method(self, form):
        """ Получаем идентификатор платежного метода """
        return settings.PAYMASTER_DEFAULT_PAYMENT_METHOD

    def get_extra_params(self, form):
        """ Дополнительные параметры продавца """
        _d = isinstance(form.data, QueryDict) and form.data.dict() or form.data
        return _d

    def init_query(self, form):
        """ Формируем параметры GET запроса """
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
            'LOC_PAYER_ID': self.get_payer_id(),
        }

        data.update(self.get_extra_params(form))

        # Сигнал посылается до создания счета (счет в дельнейшем может быть
        # проигнорирован) с параметрами инициации платежа. Этот сигнал может
        # использоваться для валидации данных (raise ValidationError).
        signals.invoice_init.send(sender=self, data=data)

        data = {k: v for k, v in data.items() if v}
        return urllib.urlencode(data)


class ConfirmView(utils.CSRFExempt, generic.View):
    """
        Обработчик предзапроса подтверждения счета (Invoice Confirmation).

        Этот HTTP POST запрос отправляется системой PayMaster на веб-сервер
        продавца, на URL, указанный в настройках, в тот момент, когда
        пользователь выбрал платежную систему и собирается производить платеж.
        Теоритически можно отказаться, однако, как указано в документации,
        запрос пользователю на оплату уходит раньше, и следовательно возможна
        ситуация, когда счет оплачен, но не принят продавцом. Чтобы избежать
        лишних отказов, в данной реализации API отказ невозможен и счет будет
        подтвержден в любом случае.

        При получении этого запроса создается счет в БД продавца и отправлется
        сигнал invoice_confirm c объектом-счетом в качестве параметра.
    """

    def post(self, request):
        # Создание счета в БД продавца
        invoice = Invoice.objects.create_from_api(request.POST)
        logger.info(u'Invoice {0} payment confirm.'.format(invoice.number))
        payer = utils.decode_payer(utils.get_request_data(request).get('LOC_PAYER_ID'))

        # Отправка сигнал подтверждения счета.
        signals.invoice_confirm.send(sender=self, payer=payer, invoice=invoice)
        return HttpResponse('YES', content_type='text/plain')


class NotificationView(utils.CSRFExempt, generic.View):
    """
        Обработчик уведомления об оплате счета (Payment Notification).

        HTTP POST запрос отправляется продавцу системой PayMaster в том случае,
        когда платеж успешно проведен. Важно понимать, что запрос Payment
        Notification - это единственный запрос, при обработке которого продавцу
        необходимо учитывать принятый платеж (оказывать услугу и т.п.).

        При получении этого запроса счет отмечается в БД как оплаченный и
        отправлется сигнал invoice_paid c объектом-счетом в качестве параметра.
    """

    _hash_fields = settings.PAYMASTER_HASH_FIELDS

    def check_hash(self, data):
        """ Проверка ключа безопасности """
        _line = u';'.join([data.get(key,'') for key in self._hash_fields])
        _line += u';{0}'.format(settings.PAYMASTER_PASSWORD)

        hash_method = settings.PAYMASTER_HASH_METHOD
        _hash = getattr(hashlib, hash_method)(_line.encode('utf-8'))
        _hash = base64.encodestring(_hash.digest()).replace('\n', '')
        return _hash == data.get('LMI_HASH')

    def post(self, request):
        if not self.check_hash(request.POST):  # Проверяем ключ
            logger.error(
                u'Invoice {0} payment failed by reason: HashError'.format(
                    request.POST.get('LMI_PAYMENT_NO')))
            return HttpResponse('HashError')

        try:
            invoice = Invoice.objects.finalize(request.POST)  # Закрываем счет

        except Invoice.InvoiceDuplication:
            logger.error(
                u'Invoice {0} payment failed by reason: Duplication'.format(
                    request.POST.get('LMI_PAYMENT_NO')))

            return HttpResponse('InvoiceDuplicationError')

        logger.info(u'Invoice {0} paid succesfully.'.format(invoice.number))
        payer = utils.decode_payer(utils.get_request_data(request).get('LOC_PAYER_ID'))

        # Отправляем сигнал об успешной оплате
        signals.invoice_paid.send(sender=self, payer=payer, invoice=invoice)
        return HttpResponse('', content_type='text/plain')


class SuccessView(utils.CSRFExempt, generic.TemplateView):
    """
        Страница успешного возврата.

        Предназначена исклчительно для уведомления пользователя об
        удачном завершении операции.

        Внимание! Этот запрос НЕ гарантирует оплаты.
    """

    def get(self, request):
        invoice = Invoice.objects.get(number=utils.get_request_data(request)['LMI_PAYMENT_NO'])
        logger.info(u'Invoice {0} success page visited'.format(invoice.number))
        signals.success_visited.send(sender=self, invoice=invoice)
        return super(SuccessView, self).get(request)

    def post(self, request):
        return self.get(request)


class FailView(utils.CSRFExempt, generic.TemplateView):
    """
        Страница неуспешного возврата.

        Предназначена исклчительно для уведомления пользователя об
        неудачном завершении операции.
    """

    def get(self, request):
        payment_no = utils.get_request_data(request)['LMI_PAYMENT_NO']

        try:
            invoice = Invoice.objects.get(number=payment_no)
            logger.info(
                u'Invoice {0} fail page visited'.format(invoice.number))

        except Invoice.DoesNotExist:
            invoice = None
            logger.error(
                u'Invoice {0} DoesNotExist'.format(payment_no))

        signals.fail_visited.send(
            sender=self, data=utils.get_request_data(request), invoice=invoice)

        return super(FailView, self).get(request)

    def post(self, request):
        return self.get(request)
