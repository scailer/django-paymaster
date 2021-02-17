# -*- coding: utf-8 -*-

from django.dispatch import Signal

invoice_init = Signal()
invoice_confirm = Signal()
invoice_paid = Signal()
success_visited = Signal()
fail_visited = Signal()
