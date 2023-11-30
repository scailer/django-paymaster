# -*- coding: utf-8 -*-

from django.urls import re_path
from . import views
from . import forms

urlpatterns = [
    re_path(r'^init/', views.InitialView.as_view(
        form_class=forms.DefaultPaymentForm,
        template_name='paymaster/init.html',
        amount_key='amount'),
        name='init'),

    re_path(r'^confirm/', views.ConfirmView.as_view(), name='confirm'),
    re_path(r'^paid/', views.NotificationView.as_view(), name='paid'),

    re_path(r'^success/',
        views.SuccessView.as_view(template_name='paymaster/success.html'),
        name='success'),

    re_path(r'^fail/',
        views.FailView.as_view(template_name='paymaster/fail.html'),
        name='fail'),
]
