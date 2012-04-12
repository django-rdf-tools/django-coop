#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

VERSION = __import__('coop').__version__

import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-coop',
    version = VERSION,
    description='A basis for a cooperative organization directory, with people, organization, offers.',
    packages=[  'coop',
                'coop.exchange',
                'coop.link',
                'coop.org',
                'coop.mailing',
                'coop.person',
                'coop.templatetags',
                'coop.utils',
                ],
    include_package_data=True,
    author='Cooperative Quinode',
    author_email='contact@quinode.fr',
    license='BSD',
    zip_safe=False,
    install_requires = ['south==0.7.3',
                        'sorl-thumbnail==11.09',
                        'django-extensions==0.6',
                        'django-admin-tools==0.4.1',
                        #'django-haystack==1.2.6',
                        #'djangoembed==0.1.1', # plutot via github
                        ],
    long_description = open('README.rst').read(),
    url = 'https://github.com/quinode/django-coop/',
    download_url = 'https://github.com/quinode/django-coop/tarball/master',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Natural Language :: English',
        'Natural Language :: French',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],

)

