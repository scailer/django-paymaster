# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from . import views
from . import forms

urlpatterns = patterns('',
    url(r'^init/', views.InitialView.as_view(
        form_class=forms.DefaultPaymentForm,
        template_name='paymaster/init.html',
        amount_key='amount'),
        name='init'),

    url(r'^confirm/', views.ConfirmView.as_view(), name='confirm'),
    url(r'^paid/', views.NotificationView.as_view(), name='paid'),

    url(r'^success/',
        views.SuccessView.as_view(template_name='paymaster/success.html'),
        name='success'),

    url(r'^fail/',
        views.FailView.as_view(template_name='paymaster/fail.html'),
        name='fail'),
)
