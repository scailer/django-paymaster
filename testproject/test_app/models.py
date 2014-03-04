# -*- coding: utf-8 -*-

from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from paymaster import signals


class User(AbstractUser):
    phone = models.CharField('Phone', max_length=25,
                             default='+7 (909) 123 4567')


class ActivityLog(models.Model):
    date = models.DateTimeField('Date', auto_now_add=True)
    invoice = models.ForeignKey('paymaster.Invoice', blank=True, null=True)
    action = models.CharField('Action', max_length=256)


@receiver(signals.invoice_init, dispatch_uid='def_init')
def _init(sender, data, **kwargs):
    if data.get('amount') == '13':
        raise ValidationError('Amount can\'t be 13')
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
