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

    def __init__(self):
        h = HotelHTMLGenerator()
    
    class TestConfig():
        def test_has_year(self):
            assert h.year is not None

    def has_valid_year(self):
        