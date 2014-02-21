# -*- coding: utf-8 -*-

from django.dispatch import Signal

invoice_init = Signal(providing_args=["data"])
invoice_confirm = Signal(providing_args=["invoice"])
invoice_paid = Signal(providing_args=["invoice"])
success_visited = Signal(providing_args=["invoice"])
fail_visited = Signal(providing_args=["invoice"])
