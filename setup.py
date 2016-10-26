#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

for cmd in ('egg_info', 'develop'):
    import sys
    if cmd in sys.argv:
        from setuptools import setup

import sys
reload(sys).setdefaultencoding("UTF-8")

setup(
    name='django-paymaster',
    version='0.2.0',
    author='Dmitriy Vlasov',
    author_email='scailer@lwr.pw',

    include_package_data=True,
    packages=['paymaster'],
    package_data={
        'paymaster': ['migrations/*.py', 'templates/paymaster/*.html']
    },

    url='https://github.com/scailer/django-paymaster/',
    license='MIT license',
    description=(u'Application for integration PayMaster payment '
                 u'system in Django projects.').encode('utf8'),
    long_description=(
        u'Приложение для интеграции платежной системы PayMaster '
        u'(http://paymaster.ru/) в проекты на Django. Реализовано '
        u'только основное API PayMaster, согласно спецификации'
        u'http://paymaster.ru/Partners/ru/docs/protocol/\n\n'
        u'С ознакомиться документацией, а так же сообщить об '
        u'ошибках можно на странице проекта '
        u'http://github.com/scailer/django-paymaster/'
    ).encode('utf8'),

    requires=['django (>= 1.5)', 'pytz', 'simple_crypt'],

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
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Russian',
    ),
)
