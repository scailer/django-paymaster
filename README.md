django-paymaster
================

Приложение для интеграции платежной системы PayMaster в проекты на Django.
Реализовано только основное API PayMaster, согласно спецификации 
[https://paymaster.ru/Partners/ru/docs/protocol](https://paymaster.ru/Partners/ru/docs/protocol).

## Установка ##

```sh
$ pip install django-paymaster
```

project/urls.py

```python
urlpatterns += i18n_patterns('',
    ...
    url(r'^paymaster/', include('paymaster.urls', namespace='paymaster')),
)
```

project/settings.py

```python
PAYMASTER_PASSWORD = '1234567890abcdef'
PAYMASTER_MERCHANT_ID = '11112222-3333-4444-5555-666677778888'
```

## Настройки ##

**Обязательные настройки**

Идентификатор сайта в системе PayMaster. Идентификатор можно увидеть в Личном Кабинете, на странице "Список сайтов", в первой колонке.
```python
PAYMASTER_MERCHANT_ID = '11112222-3333-4444-5555-666677778888'
```

Пароль сайта в системе PayMaster.
```python
PAYMASTER_PASSWORD = '1234567890abcdef'

Маска описания платежа, где payer - django-пользователь, number - номер платежа.
```python
PAYMASTER_DESCRIPTION_MASK = u'Пополнение баланса для пользователя {payer.email} [{number}]'
```


**Финансовые параметры**

Идентификатор валюты платежа, принимаемой продавцом.
```python
PAYMASTER_MERCHANT_CURRENCY = 'RUB', 'EUR'
```

Идентификатор платежного метода, выбранный по умолчанию.
```python
PAYMASTER_DEFAULT_PAYMENT_METHOD = 'WebMoney'
```


**Безопасность**

Метод хеширования указанный в настройках
```python
PAYMASTER_HASH_METHOD = 'md5', 'sha1', 'sha256'
```

Список полей для хеширования
```python
HASH_FIELDS = (
    'LMI_MERCHANT_ID', 'LMI_PAYMENT_NO', 'LMI_SYS_PAYMENT_ID',
    'LMI_SYS_PAYMENT_DATE', 'LMI_PAYMENT_AMOUNT', 'LMI_CURRENCY',
    'LMI_PAID_AMOUNT', 'LMI_PAID_CURRENCY', 'LMI_PAYMENT_SYSTEM',
    'LMI_SIM_MODE'
)
```


**Тестирование**

Дополнительное поле, определяющее режим тестирования.
```python
PAYMASTER_SIM_MODE = 0, 1, 2
```

Ссылка для инициации платежа.
```python
PAYMASTER_INIT_URL = 'https://paymaster.ru/Payment/Init'
```

Если присутствует, то запрос Invoice Confirmation будет отправляться по указанному URL (а не установленному в настройках).
```python
PAYMASTER_INVOICE_CONFIRMATION_URL = 'http://myhost.ru/paymaster/confirm/'
```

Если присутствует, то запрос Payment Notification будет отправляться по указанному URL (а не установленному в настройках).
```python
PAYMASTER_PAYMENT_NOTIFICATION_URL = 'http://myhost.ru/paymaster/notification/'
```

Если присутствует, то при успешном платеже пользователь будет отправлен по указанному URL (а не установленному в настройках).
```python
PAYMASTER_SUCCESS_URL = 'http://myhost.ru/paymaster/success/'
```

Если присутствует, то при отмене платежа пользователь будет отправлен по указанному URL (а не установленному в настройках).
```python
PAYMASTER_FAILURE_URL = 'http://myhost.ru/paymaster/fail/'
```


**Дополнительные настройки**

Атрибут объекта django-пользователя в котором содержиться номер телефона
```python
PAYMASTER_USER_PHONE_FIELD = 'phone'
```

Атрибут объекта django-пользователя в котором содержиться эл. почта
```python
PAYMASTER_USER_EMAIL_FIELD = 'email'
```

Внешний идентификатор магазина, передаваемый интегратором в платежную систему.
```python
PAYMASTER_SHOP_ID = '123456'
```

## Сигналы ##

```python
from django.db import models
from django.dispatch import receiver
from paymaster import signals


class ActivityLog(models.Model):
    date = models.DateTimeField('Date', auto_now_add=True)
    invoice = models.ForeignKey('paymaster.Invoice', blank=True, null=True)
    action = models.CharField('Action', max_length=256)


@receiver(signals.invoice_init, dispatch_uid='def_init')
def _init(sender, data, **kwargs):
    if data.get('amount'):
        ActivityLog.objects.create(action='init')


@receiver(signals.invoice_confirm, dispatch_uid='def_confirm')
def _confirm(sender, invoice, **kwargs):
    ActivityLog.objects.create(action='confirm', invoice=invoice)


@receiver(signals.invoice_paid, dispatch_uid='def_paid')
def _paid(sender, invoice, **kwargs):
    ActivityLog.objects.create(action='paid', invoice=invoice)


@receiver(signals.success_visited, dispatch_uid='def_success')
def _success(sender, invoice, **kwargs):
    ActivityLog.objects.create(action='success', invoice=invoice)


@receiver(signals.fail_visited, dispatch_uid='def_fail')
def _fail(sender, invoice, **kwargs):
    ActivityLog.objects.create(action='fail', invoice=invoice)
```


## Кастомизация ##

```python
from django import forms
from django.conf.urls import patterns, url
from paymaster import views

choices = (('WebMaster', 'WebMaster'),)


class CustomForm(forms.Form):
    payment_method = forms.CharField(
        label=u'Плетежная система', choices=choices)
    amount = forms.DecimalField(
        label=u'Сумма', min_value=10, required=True)


class CustomInitialView(views.InitialView):
    def get_payer(self):
        return self.request.user

    def get_description(self, form):
        return u'Новое описание'

    def get_payer_phone(self, form):
        return u'89091239876'

    def get_payer_email(self, form):
        return u'mail@mail.ru'

    def get_payment_method(self, form):
        return form.data.get('payment_method')


urlpatterns = patterns('',
    url(r'^init/', views.CustomInitialView.as_view(
        form_class=forms.DefaultPaymentForm,
        template_name='paymaster/init.html',
        amount_key='amount'), name='init'),
)
```
