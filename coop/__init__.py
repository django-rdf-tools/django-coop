# -*- coding: utf-8 -*-

VERSION = (0, 7, 5)


def get_version():
    return '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])

__version__ = get_version()


