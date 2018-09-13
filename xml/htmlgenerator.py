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
from os.path import expanduser
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

    def __init__(self, search_directory = None, output_directory = None, year = "2018"):
        self.search_directory = search_directory or "/home/dan/Documents/lantera/xml/search"
        self.output_directory = output_directory or "/home/dan/Documents/lantera/xml"
        self.SEARCH_FILENAME = 'rates.input.xml'  # Constant for our search file

        # Set the year to 2018 AD unless otherwise
        # specified in the arguments
        if ("--year" in args):
            self.year = args[args.index("--year") + 1]
        else:
            self.year = year

        # Shorthand/aliases for directories
        self.sdir = self.search_directory
        self.odir = self.output_directory

        # An attribute to hold the paths to discovered search results
        self.paths =  [self._convert_dirs_to_absolute(x) for x in self.scan()]

        if len(args) is 1:
                print("Script was called with no arguments. If you need info, invoke the script with -h or --help")

        if ("-h" in args) or ("--help" in args):
            self.help()

        if ("--relative" not in args):
            self._convert_dirs_to_absolute(self.dirs())


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
Pass --relative to disable conversion of relative paths to absolute paths. Pass --year (4 digit year) to use a year other than 2018. Pass -h or --help to print this message""".format(args[0], linesep)
        print(helpText)
        raise SystemExit()

    def _convert_dirs_to_absolute(self, iterable):
        ''' Used in several contexts to convert lists of directories which may
        have relative paths to their absolute counterparts'''
        if (type(iterable) == dict):
            print(iterable)
            for val in iterable:
                print(val)
                if val in ["~", "~/"]:
                    val = expanduser("~")
                if val in [".", "./"]:
                    val = getcwd()
                if val.startswith("./"):
                    val = path.join(getcwd(), val[2:])
                val = path.normpath(val)
                try:
                    assert (path.exists(val) and path.isdir(val))
                    iterable[key] = val
                    print("Relative path of {0} changed from {1} to {2}".format(key, val, val))
                except AssertionError:
                    print("Error converting relative path of {0} from {1} to {2}. Sticking with relative path.".format(key,val))
            return iterable
        if (type(iterable) == list):
            for val in iterable:
                if val in ["~", "~/"]:
                    val = expanduser("~")
                if val in [".", "./"]:
                    val = getcwd()
                if val.startswith("./"):
                    val = path.join(getcwd(), val[2:])
                val = path.normpath(val)
                try:
                    assert (path.exists(val) and path.isdir(val))
                    print("Relative path of {0} changed from {1} to {2}".format(key, val, val))
                except AssertionError:
                    print("Error converting path of {0}. Sticking with relative path.".format(val))
            return iterable
        if type(iterable == str):
            val = iterable
            if val in ["~", "~/"]:
                val = expanduser("~")
            if val in [".", "./"]:
                val = getcwd()
            if val.startswith("./"):
                val = path.join(getcwd(), val[2:])
            val = path.normpath(val)
            try:
                assert (path.exists(val) and path.isdir(val))
                print("Relative path changed from {1} to {2}".format(iterable, val))
            except AssertionError:
                print("Error converting path of {0}. Sticking with relative path.".format(val))
            finally:
                return val



    def dirs(self):
        ''' Get a hash of the directories we are using. '''
        return {"search_directory": self.search_directory, "output_directory": self.output_directory}

    def getArgs(self):
        ''' Get an enumerated list comprehension of the arguments the program was called with. '''
        return [arg for arg in enumerate(args)]

    def scan(self):
        ''' Generator which scans recursively for a rates.input.xml file and yields their paths '''

        paths = []

        if not path.exists(self.search_directory):
            raise SystemExit("Specified search directory does not exist.")

        for root, dirs, files in walk(self.search_directory):

            # Make the search case insensitive by converting everything to lower case
            files = [file.lower() for file in files]

            template = Template("root: $root, dirs: $dirs, files: $files").substitute(
                {'root': root, 'dirs': dirs, 'files': files})
            print(template, end=linesep)

            # Look for our XML file in among the files in the current directory
            if self.SEARCH_FILENAME in files:
                # Assemble a full, absolute path
                fullpath = path.join(root, self.SEARCH_FILENAME)

                # Detect symlinks
                try:
                    assert not path.islink(fullpath)
                except AssertionError as e:
                    print("Search result is a symlink (shortcut). Will use real path instead.")
                    fullpath = path.realpath(fullpath)

                # Verify we are actually pointing toward a file
                try:
                    assert path.isfile(fullpath)
                except AssertionError as e:
                    print("OS reports search result at {0} is not an actual file. Trying to continue...".format(fullpath))
                    continue

                print("Found {0} in {1}".format(self.SEARCH_FILENAME, fullpath))
                paths.append(fullpath)


                yield fullpath

    def parse(self):
        ''' Return a parser object with the XML markup from the file '''
        if not path.exists(xmlfile) or not path.isfile(xmlfile):
            raise SystemExit("Generate HTML function was called with an invalid path or file.")
        try:
            with open(xmlfile, 'r') as file:
                contents = file.read()
                print(contents)
                return bs4.BeautifulSoup(contents, "lxml")
        except IOError:
            raise SystemExit("Unable to read found XML file.")




if (__name__ == "__main__"):
    if len(args) == 3:
        h = HotelHTMLGenerator(args[1], args[2])
    else:
        h = HotelHTMLGenerator()
    print("\narguments: ", str(h.getArgs()), end="\n\n")
    print("\npaths: ", [x for x in h.scan()], end="\n\n")
