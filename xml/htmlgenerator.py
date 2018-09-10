#!/usr/bin/python
from __future__ import print_function # Python 2/3 compatibility
'''
@author Dan Mercurio <dmercurio92@gmail.com>

Traverse a directory searching for a rates.input.xml file
and for each directory containing this file, produce two HTML files
(rate-chart.html and rate-month.html) with greater detail of
the hotel rates across month intervals.
'''

from os import walk, linesep, path, getcwd
from os.path import join, getsize, expanduser
from sys import argv as args, stdout, version_info

class HotelHTMLGenerator(object):

    def __init__(self, search_directory = None, output_directory = None):
        self.search_directory = search_directory or "/home/dan/Documents/lantera/xml/search"
        self.output_directory = output_directory or "/home/dan/Documents/lantera/xml"

        # Shorthand/aliases for directories
        self.sdir = self.search_directory
        self.odir = self.output_directory

        if len(args) is 1:
                print("Script was called with no arguments. If you need info, invoke the script with -h or --help")

        if ("-h" in args) or ("--help" in args):
            self.help()

        if ("--relative" not in args):
            self.convertDirsToAbsolute()

    def _print(self, text, appendNewline = True):
        try:
            assert type(text) is str
            if (appendNewline):
                stdout.write(text)
                stdout.write(linesep)
            else:
                stdout.write(text)
        except AssertionError:
            raise SystemExit("Called _print with non-string as argument")

    def help(self):
        helpText = """Usage: python {0} [search directory] [output directory] [--arguments (optional)]{1}
Pass --relative to disable conversion of relative paths to absolute paths. Pass -h or --help to print this message""".format(args[0], linesep)
        print(helpText)
        raise SystemExit()

    def convertDirsToAbsolute(self):
        for key, val in self.dirs().items():
            if val in ["~", "~/"]:
                newVal = expanduser("~")
            if val in [".", "./"]:
                newVal = getcwd()
            if val.startswith("./"):
                newVal = path.join(getcwd(), val[2:])
            newVal = path.normpath(newVal)
            try:
                assert path.exists(newVal) and path.isdir(newVal)
                self.__setattr__(key, newVal)
            except AssertionError:
                print("Error converting relative path of {0} from {1} to {2}. Sticking with relative path.".format(key, val, newVal))
                pass
            print("Relative path of {0} changed from {1} to {2}".format(key, val, newVal))


    def dirs(self):
        ''' Get a hash of the directories we are using. '''
        return {"search_directory": self.search_directory, "output_directory": self.output_directory}

    def getArgs(self):
        ''' Get an enumerated list comprehension of the arguments the program was called with. '''
        return [arg for arg in enumerate(args)]

    def scan(self):
        ''' Scan recursively for a rates.input.xml file and return its path '''
        if not path.exists(self.search_directory):
            raise SystemExit("Specified search directory does not exist.")

        for root, dirs, files in walk(self.search_directory):
            print("Searching directory: ".format(root))
            print( root, "consumes")
            print( sum([getsize(join(root, name)) for name in files]))
            print( "bytes in", len(files), "non-directory files")

if (__name__ == "__main__"):
    if len(args) == 3:
        h = HotelHTMLGenerator(args[1], args[2])
    else:
        h = HotelHTMLGenerator()
    print("arguments: ", str(h.getArgs()))
    #h.scan()
