#!/usr/bin/python

'''
@author Dan Mercurio <dmercurio92@gmail.com>

Traverse a directory searching for a rates.input.xml file
and for each directory containing this file, produce two HTML files
(rate-chart.html and rate-month.html) with greater detail of
the hotel rates across month intervals.
'''

from os import walk, path
from sys import argv as args, stdout

class HotelHTMLGenerator(object):

    def __init__(self, search_directory = None, output_directory = None):
        self.search_directory = search_directory or "/home/dan/Documents/lantera/xml/search"
        self.output_directory = output_directory or "/home/dan/Documents/lantera/xml"

        if len(args) is 1:
                self._print("Script was called with no arguments. If you need info, \
                    invoke the script with -h or --help")

        if "-h" or "--help" in args:
            self.help()

    def _print(self, text):
        ''' This is for 2/3 compatibility. '''
        with open(stdout, "w") as out:
            out.write(text)

    def help(self):
        helpText = """Usage: python {0} [search directory] [output directory]""".format(args[0])
        self._print(helpText)
        raise SystemExit()

    def dirs(self):
        ''' Get a hash of the directories we are using. '''
        return {"search": self.search_directory, "output": self.output_directory}

    def scan(self):
        if not path.exists(self.search_directory):
            raise SystemExit('Directory doesn\'t exist.')

if (__name__ == "__main__"):
    if len(args) > 1:
        h = HotelHTMLGenerator(args[1], args[2])
    else:
        h = HotelHTMLGenerator()
    print(h.dirs())
