#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

for cmd in ('egg_info', 'develop'):
    import sys
    if cmd in sys.argv:
        from setuptools import setup



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
    description=(),
    long_description=(),

    requires=['django (>= 1.5)', 'pytz', 'simple_crypt'],

    classifiers=(b'test',),
)
