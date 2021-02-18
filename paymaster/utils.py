# -*- coding: utf-8 -*-

import base64
from uuid import uuid4
from datetime import datetime

from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from . import logger


def decode_payer(enc):
    """ Декодирование пользователя-инициатора платежа """
    try:
        return get_user_model().objects.get(pk=enc)

    except get_user_model().DoesNotExist:
        logger.warn(u'Payer does not exist')


def encode_payer(user):
    """ Кодирование пользователя-инициатора платежа """
    return str(user.pk)


def number_generetor(view, form):
    """ Генератор номера платежа (по умолчанию) """
    return u'{:%Y%m%d}-{:08x}'.format(datetime.now(), uuid4().fields[0])


class CSRFExempt(object):

    """ Mixin отключения проверки CSRF ключа """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CSRFExempt, self).dispatch(*args, **kwargs)
