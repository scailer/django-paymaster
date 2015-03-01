# -*- coding: utf-8 -*-

import base64
from uuid import uuid4
from datetime import datetime
from simplecrypt import encrypt, decrypt, DecryptionException

from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from . import settings
from . import logger


def decode_payer(enc):
    """ Декодирование пользователя-инициатора платежа """
    try:
        secret = base64.decodestring(enc.encode('utf-8'))
        pk = decrypt(settings.SECRET_KEY, secret)
        return get_user_model().objects.get(pk=pk)

    except DecryptionException:
        logger.warn(u'Payer decryption error')

    except get_user_model().DoesNotExist:
        logger.warn(u'Payer does not exist')


def encode_payer(user):
    """ Кодирование пользователя-инициатора платежа """
    secret = encrypt(settings.SECRET_KEY, u"{}".format(user.pk))
    return base64.encodestring(secret).decode('utf-8')


def number_generetor(view, form):
    """ Генератор номера платежа (по умолчанию) """
    return u'{:%Y%m%d}-{:08x}'.format(datetime.now(), uuid4().fields[0])


class CSRFExempt(object):

    """ Mixin отключения проверки CSRF ключа """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CSRFExempt, self).dispatch(*args, **kwargs)
