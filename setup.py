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
    version='0.1-alpha',
    author='Dmitriy Vlasov',
    author_email='scailer@russia.ru',

    packages=['paymaster', 'paymaster.migrations', 'paymaster.templates'],
    include_package_data=True,

    url='https://github.com/scailer/django-paymaster/',
    license = 'MIT license',
    description = u'Приложение для интеграции платежной системы PayMaster в проекты на Django.'.encode('utf8'),
    long_description = open('README.md').read().decode('utf8') + u"\n\n" + open('CHANGES.md').read().decode('utf8'),

    requires=['django (>= 1.5)', 'pytz'],

    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
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
