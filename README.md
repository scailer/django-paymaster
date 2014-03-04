django-paymaster
================

Приложение для интеграции платежной системы PayMaster в проекты на Django.
Реализовано только основное API PayMaster, согласно спецификации 
[https://paymaster.ru/Partners/ru/docs/protocol](https://paymaster.ru/Partners/ru/docs/protocol).

## Установка ##

```sh
$ pip install django simple_crypt pytz django-paymaster
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

LOGGING = {
    ...
    'loggers': {
        ...
        'paymaster': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
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
```

Маска описания платежа, где payer - django-пользователь, number - номер платежа.
```python
PAYMASTER_DESCRIPTION_MASK = u'Платеж пользователя {payer.email} [{number}]'
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
PAYMASTER_HASH_FIELDS = (
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

Функция-генератор номеров счетов
```python
def foo(view, form):
    return unicode(1)

PAYMASTER_INVOICE_NUMBER_GENERATOR = foo
```

## Сигналы ##

**`signals.invoice_init`**

Сигнал посылается до создания счета (счет в дельнейшем может быть
проигнорирован) с параметрами инициации платежа. Этот сигнал может
использоваться для валидации данных (raise ValidationError).

Аргуметы:

data = request.REQUEST

**`signals.invoice_confirm`**

Сигнал посылается после создания счета но до регистрации его оплаты 
с объектом-счетом и плательщиком в качестве аргумента. Используется 
для действий предваряющих оплату (уведомления, логирование и т.п.)

Аргуметы:

payer = Django-пользователь, инициатор платежа

invoice = paymaster.models.Invoice

**`signals.invoice_paid`**

Сигнал посылается после оплаты счета с объектом-счетом в качестве 
аргумента. Используется для предоставления услуги продавцом. 
Является единственным безопасным сигналом, гарантирущим что счет
оплачен.

Аргуметы:

payer = Django-пользователь, инициатор платежа

invoice = paymaster.models.Invoice

**`signals.success_visited`**

Сигнал посылается до отображения пользователю страницы-уведомления
об успешном проведении платежа. НЕ гарантирует безопасности и 
валидности платежа, служит исключительно в целях 
уведомления/логирования.

Аргуметы:

data = request.REQUEST

invoice = paymaster.models.Invoice

**`signals.fail_visited`**

Сигнал посылается до отображения пользователю страницы-уведомления
об неуспешном проведении платежа. Служит исключительно в целях 
уведомления/логирования.

Аргуметы:

data = request.REQUEST

invoice = paymaster.models.Invoice


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
def _confirm(sender, payer, invoice, **kwargs):
    sender.request.user  # sender is view-class object
    ActivityLog.objects.create(action='confirm', invoice=invoice)


@receiver(signals.invoice_paid, dispatch_uid='def_paid')
def _paid(sender, payer, invoice, **kwargs):
    ActivityLog.objects.create(action='paid', invoice=invoice)


@receiver(signals.success_visited, dispatch_uid='def_success')
def _success(sender, data, invoice, **kwargs):
    ActivityLog.objects.create(action='success', invoice=invoice)


@receiver(signals.fail_visited, dispatch_uid='def_fail')
def _fail(sender, data, invoice, **kwargs):
    ActivityLog.objects.create(action='fail', invoice=invoice)
```


## Шаблоны ##

**`paymaster/init.html`**

Шаблон формы платежа, форма в контексте под именем "form".

```html
<form action="{% url "paymaster:init" %}" method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="submit" value="Send" />
</form>
```

**`paymaster/success.html`**

Шаблон уведобления об успешном платеже.

**`paymaster/fail.html`**

Шаблон уведобления о неудачном платеже.


## Кастомизация ##

```python
from django import forms
from django.conf.urls import patterns, url
from paymaster import views

choices = (('WebMaster', 'WebMaster'),)


class CustomForm(forms.Form):
    payment_method = forms.CharField(
        label=u'Плетежная система', choices=choices)
    amount_value = forms.DecimalField(
        label=u'Сумма', min_value=10, required=True)


class CustomInitialView(views.InitialView):
    def get_payer(self):
        # Плательщик, как правило текущий пользователь.
        # Используется для получения информации о телефоне 
        # и электронной почте плательщика, а так же передается
        # в строку-шаблон назначения платежа
        return self.request.user

    def get_description(self, form):
        # Назначение платежа, по умолчанию формируется по шаблону 
        # настройках проекта PAYMASTER_DESCRIPTION_MASK
        # Внимание: В соответствии с условиями договора c PayMaster, 
        # назначение платежа должно быть детализированным: следует 
        # указывать название конкретной предоставляемой услуги, 
        # номер лицевого (торгового) счета или аналогичную информацию, 
        # позволяющую установить оказываемую услугу или 
        # предоставляемый товар. LMI_PAYMENT_DESC (не более 255 символов)
        return u'Новое описание'

    def get_payer_phone(self, form):
        # Номер телефона плательщика в цифровом формате
        # LMI_PAYER_PHONE_NUMBER
        return u'89091239876'

    def get_payer_email(self, form):
        # Email плательщика LMI_PAYER_EMAIL
        return u'mail@mail.ru'

    def get_payment_method(self, form):
        # Идентификатор платежного метода, выбранный 
        # пользователем. LMI_PAYMENT_METHOD
        return form.data.get('payment_method')

    # Аналогичным образом могут быть переопределены 
    # get_amount - сумма платежа, 
    # get_paymant_no - номер платежа,
    # get_extra_params - дата истечения актуальности счета


urlpatterns = patterns('',
    url(r'^init/', views.CustomInitialView.as_view(
        form_class=CustomForm,
        template_name='paymaster/init.html',
        email_field='email',  # атрибут объекта-плательщика содержащий эл.почту
        phone_field='phone',  # атрибут объекта-плательщика содержащий номер телефона
        amount_key='amount_value'),  # имя поля формы со значением суммы платежа
        name='init'),

    url(r'^success/',
        views.SuccessView.as_view(template_name='paymaster/success.html'),
        name='success'),

    url(r'^fail/',
        views.FailView.as_view(template_name='paymaster/fail.html'),
        name='fail'),

)
```
