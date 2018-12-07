#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

@author Dan Mercurio <dmercurio92@gmail.com>
@date 11/29/2018

"""

import htmlgenerator
import pytest


class HTMLGeneratorTest(unittest.TestSuite):
    """ A test suite for our singleton hotel HTML processor object """

    def setUp(self):
        """ Just instantiate the object so we can run tests on it. """    
        self._testClass = h =htmlgenerator.HotelHTMLGenerator()

    class TestConfig():
        def test_has_year(self):
            """ Test that a year value is present and valid. """
            assert self._testClass.year is not None


        def has_valid_year(self):
            """ Test that the year value is valid, or the calendar will not be generated properly."""
            assert type(self._testClass.year) is int and len(str(self._testClass.year)) == 4