# -*- coding: utf-8 -*-

import sys
from uuid import uuid4
from datetime import datetime
from simplecrypt import encrypt, decrypt, DecryptionException
import binascii

from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from . import settings
from . import logger


def decode_payer(enc):
    """ Декодирование пользователя-инициатора платежа """
    if enc is None:
        return None
    try:
        #_chr = ''.join(chr(int(enc[i:i + 3])) for i in range(0, len(enc), 3))
        _chr = binascii.unhexlify(enc)
        pk = decrypt(settings.SECRET_KEY, _chr)

        return get_user_model().objects.get(pk=int(pk))

    except DecryptionException:
        logger.warn(u'Payer decryption error{}'.format(enc))
        logger.warn(u'Payer error{}'.format(DecryptionException))

    except get_user_model().DoesNotExist:
        logger.warn(u'Payer does not exist')


def encode_payer(user):
    """ Кодирование пользователя-инициатора платежа """
    secret = encrypt(settings.SECRET_KEY, str(user.pk))
    return binascii.hexlify(secret)
    #return u''.join(u'{0:03}'.format(x) for x in secret)


def number_generetor(view, form):
    """ Генератор номера платежа (по умолчанию) """
    return u'{:%Y%m%d}-{:08x}'.format(datetime.now(), uuid4().fields[0])

def get_request_data(request):
    """Получение данных, передаваемых с запросом"""
    if request.method == 'POST':
        return request.POST
    else:
        return request.GET


class CSRFExempt(object):
    """ Mixin отключения проверки CSRF ключа """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CSRFExempt, self).dispatch(*args, **kwargs)
    
