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
    name = 'django-coop',
    version = VERSION,
    description = 'A basis for a cooperative organization directory, with people, organization, offers.',
    packages = ['coop',
                'coop.bin',
                'coop.management',
                'coop.management.commands',
                'coop.article',
                'coop.exchange',
                'coop.link',
                'coop.org',
                'coop.mailing',
                'coop.agenda',
                'coop.agenda.conf',
                'coop.person',
                'coop.prefs',
                'coop.project',
                'coop.tag',
                'coop.templatetags',
                'coop.utils',
                'coop.webid',
                'coop.ui',
                'coop.rdf',
                ],
    include_package_data = True,
    author = 'Cooperative Quinode',
    author_email = 'contact@quinode.fr',
    license = 'BSD',
    zip_safe = False,
    install_requires = ['south', 'django',
                        'sorl-thumbnail==11.09',
                        #'django-extensions==0.8',  # waiting for new Pypi version with our 12/09/12 commit
                        #'django-admin-tools==0.4.1', # for 1.4 : waiting for merging of https://bitbucket.org/psyton/django-admin-tools
                        #'django-haystack==1.2.6', # github dev version needed
                        #'djangoembed==0.1.1', # Pypi: bad version, we use: https://github.com/ericflo/django-oembed
                        ],
    long_description = open('README.rst').read(),
    url = 'https://github.com/quinode/django-coop/',
    download_url = 'https://github.com/quinode/django-coop/tarball/master',
    scripts = [
        'coop/bin/coop-admin.py',
        'coop/bin/runinenv.sh'],
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
