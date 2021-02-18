#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from distutils.core import setup

for cmd in ('egg_info', 'develop'):
    if cmd in sys.argv:
        from setuptools import setup

try:
    reload(sys).setdefaultencoding("UTF-8")
except:
    pass

setup(
    name='django-paymaster',
    version='1.0.0',
    author='Dmitriy Vlasov',
    author_email='scailer@russia.ru',

    include_package_data=True,
    packages=['paymaster'],
    package_data={
        'paymaster': ['migrations/*.py', 'templates/paymaster/*.html']
    },

    url='https://github.com/scailer/django-paymaster/',
    license='MIT license',
    description=(u'Application for integration PayMaster payment '
                 u'system in Django projects.'),
    long_description=(
        u'Приложение для интеграции платежной системы PayMaster '
        u'(http://paymaster.ru/) в проекты на Django. Реализовано '
        u'только основное API PayMaster, согласно спецификации'
        u'http://paymaster.ru/Partners/ru/docs/protocol/\n\n'
        u'С ознакомиться документацией, а так же сообщить об '
        u'ошибках можно на странице проекта '
        u'http://github.com/scailer/django-paymaster/'
    ),

    requires=['django (>= 3.1.1)', 'pytz'],

    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Russian',
    ),
)
