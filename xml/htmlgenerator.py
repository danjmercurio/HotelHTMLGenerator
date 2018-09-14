#!/usr/bin/python
from __future__ import print_function # Python 2/3 compatibility
'''
@author Dan Mercurio <dmercurio92@gmail.com>

Traverse a directory searching for a rates.input.xml file
and for each directory containing this file, produce two HTML files
(rate-chart.html and rate-month.html) with greater detail of
the hotel rates across month intervals.
'''

from os import walk, linesep, getcwd
import os.path
from sys import argv as args, stdout
from string import Template
try:
    import yattag
except ImportError:
    raise SystemExit("HTML generator package yattag not found. Run pip install --user yattag")
try:
    import bs4
except ImportError:
    raise SystemExit("XML parser package bs4 not found. Run pip install --user bs4")
try:
    import lxml
except ImportError:
    raise SystemExit("XML parser backend package lxml not found. Run pip install --user lxml")


class HotelHTMLGenerator(object):

    def __init__(self, search_directory = "./search", output_directory = "./output", year = "2018"):
        # First check if we are just displaying help text
        if ("-h" in args) or ("--help" in args):
            self.help()

        if len(args) is 1:
            print("Script was called with no arguments. If you need info, invoke the script with -h or --help")
            raise SystemExit



        self.dirs = dict()
        initial_dirs = {
            'search_directory': search_directory,
            'output_directory': output_directory
        }

        self.setDirs(initial_dirs)

        self.SEARCH_FILENAME = 'rates.input.xml'  # Constant for our search file

        # Set the year to 2018 AD unless otherwise
        # specified in the arguments
        if ("--year" in args):
            self.year = args[args.index("--year") + 1]
        else:
            self.year = year        

        if ("--relative" not in args):
            absolute_dirs = [self._convert_directory_to_absolute(val) for val in self.getDirs().values()]
            self.setDirs({'output_directory': absolute_dirs[0], 'search_directory': absolute_dirs[1]})

        # An attribute to hold the paths to discovered search results
        self.paths = [self._convert_directory_to_absolute(x) for x in self.scan()]

        self.parse(self.paths)


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
        helpText = """Usage: python[3] {0} [search directory] [output directory] [--arguments (optional)]{1}
Pass --relative to disable conversion of relative paths to absolute paths. Pass --year (4 digit year) to use a year other than 2018. Pass -h or --help to print this message""".format(args[0], linesep)
        print(helpText)
        raise SystemExit()

    def _convert_directory_to_absolute(self, directory):
        ''' Used in several contexts to convert lists of directories which may
        have relative paths to their absolute counterparts'''
        return os.path.realpath(directory)



    def getDirs(self):
        ''' Get a hash of the directories we are using. '''
        return self.dirs

    def setDirs(self, dirs):
        try:
            assert isinstance(dirs, dict)
            self.dirs['search_directory'] = dirs['search_directory']
            self.dirs['output_directory'] = dirs['output_directory']
            return self.dirs
        except AssertionError:
            print("Attempted to set directories to a non-dictionary object")
            raise SystemExit
        except KeyError:
            raise SystemExit("Attempted to set directories with a dictionary of invalid keys")

    def getArgs(self):
        ''' Get an enumerated list comprehension of the arguments the program was called with. '''
        return [arg for arg in enumerate(args)]

    def scan(self):
        ''' Generator which scans recursively for a rates.input.xml file and yields their paths '''

        if not os.path.exists(self.getDirs()['search_directory']):
            raise SystemExit("Specified search directory does not exist.")

        for root, dirs, files in walk(self.getDirs()['search_directory']):

            # Make the search case insensitive by converting everything to lower case
            files = [file.lower() for file in files]

            # Look for our XML file in among the files in the current directory
            if self.SEARCH_FILENAME in files:
                # Assemble a full, absolute path
                fullpath = os.path.join(root, self.SEARCH_FILENAME)

                # Detect symlinks
                try:
                    assert not os.path.islink(fullpath)
                except AssertionError as e:
                    print("Search result is a symlink (shortcut). Will use real path instead.")
                    fullpath = os.path.realpath(fullpath)
                    continue
                # Verify we are actually pointing toward a file
                try:
                    assert os.path.isfile(fullpath)
                except AssertionError as e:
                    print("OS reports search result at {0} is not an actual file. Trying to continue...".format(fullpath))
                    continue

                print("Found {0} at {1}".format(self.SEARCH_FILENAME, fullpath))

                yield fullpath

    def parse(self, paths):
        ''' Parse XML files at each found path. Generate HTML from each parser object, and output it'''
        for xmlfile in paths: 
            if not os.path.exists(xmlfile) or not os.path.isfile(xmlfile):
                raise SystemExit("Generate HTML function was called with an invalid path or file.")
            try:
                with open(xmlfile, 'r') as file:
                    contents = file.read()
                    soup = bs4.BeautifulSoup(contents, "lxml")
                    print(soup.prettify())
            except IOError:
                raise SystemExit("Unable to read found XML file.")

if (__name__ == "__main__"):
    if len(args) == 3:
        h = HotelHTMLGenerator(args[1], args[2])
    else:
        h = HotelHTMLGenerator()
    #print("\narguments: ", str(h.getArgs()), end="\n\n")
    #print("\npaths: ", [x for x in h.scan()], end="\n\n")
