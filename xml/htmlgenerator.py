#!/usr/bin/python3.7

'''
@author Dan Mercurio <dmercurio92@gmail.com>

Traverse a directory searching for a rates.input.xml file
and for each directory containing this file, produce two HTML files
(rate-chart.html and rate-month.html) with greater detail of
the hotel rates across month intervals.
'''

from os import walk, path

class HotelHTMLGenerator(object):

    def __init__(self, search_directory, output_directory):
        self.search_directory = search_directory
        self.output_directory = output_directory

    def scan(self):
        if not path.exists(self.search_directory):
            raise SystemExit('Directory doesn\'t exist.')


