#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

@author Dan Mercurio <dmercurio92@gmail.com>
@date 11/29/2018

"""

import pytest
import htmlgenerator

class HTMLGeneratorTest(unittest.TestSuite):
    """ A test suite for our singleton hotel HTML processor object """

    def setUp(self):
        """ Just instantiate the object so we can run tests on it. """ 

                # Fix for problems with PATH variable
        import sys, os
        myPath = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, myPath + '/../')
   
        self._testClass = h =htmlgenerator.HotelHTMLGenerator()

    class TestConfig():
        def test_has_year(self):
            """ Test that a year value is present and valid. """
            assert self._testClass.year is not None


        def has_valid_year(self):
            """ Test that the year value is valid, or the calendar will not be generated properly."""
            assert type(self._testClass.year) is int and len(str(self._testClass.year)) == 4