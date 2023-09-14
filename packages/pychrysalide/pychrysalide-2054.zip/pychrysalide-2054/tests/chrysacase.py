#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


import unittest
import os
import sys


class ChrysalideTestCase(unittest.TestCase):
    """Base class for all Chrysalide test cases."""

    @classmethod
    def setUpClass(cls):

        fullname = sys.modules[ChrysalideTestCase.__module__].__file__
        filename = os.path.basename(fullname)

        cls._baselen = len(fullname) - len(filename)


    def shortDescription(self):
        """Discard the direct use of __doc__ strings."""

        return None


    def __str__(self):
        """Display the description of the current tested case."""

        fullname = sys.modules[self.__class__.__module__].__file__

        origin = fullname[self._baselen:]

        title = self._testMethodDoc and self._testMethodDoc or self._testMethodName

        return '[%s] "%s"' % (origin, title)


    @classmethod
    def log(cls, msg):
        """Display an information message."""

        fullname = sys.modules[cls.__module__].__file__

        origin = fullname[cls._baselen:]

        print('[%s] *** %s ***' % (origin, msg))
