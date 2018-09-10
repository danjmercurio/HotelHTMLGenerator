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
class HotelHTMLGenerator(object):

    def __init__(self, search_directory = None, output_directory = None):
        self.search_directory = search_directory or "/home/dan/Documents/lantera/xml/search"
        self.output_directory = output_directory or "/home/dan/Documents/lantera/xml"
        self.SEARCH_FILENAME = 'rates.input.xml'  # Constant for our search file

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
                val = expanduser("~")
            if val in [".", "./"]:
                val = getcwd()
            if val.startswith("./"):
                val = path.join(getcwd(), val[2:])
            val = path.normpath(val)
            try:
                assert path.exists(val) and path.isdir(val)
                self.__setattr__(key, val)
            except AssertionError:
                print("Error converting relative path of {0} from {1} to {2}. Sticking with relative path.".format(key,
                                                                                                                   val,
                                                                                                                   val))
                pass
            print("Relative path of {0} changed from {1} to {2}".format(key, val, val))


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
            template = Template("root: $root, dirs: $dirs, files: $files").substitute(
                {'root': root, 'dirs': dirs, 'files': files}).replace(',', linesep)
            print(template, end=linesep)

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
                    print("Search result at is not an actual file.".format(fullpath))
                    continue

                print("Found {0} in {1}".format(self.SEARCH_FILENAME, fullpath))
                return path.normpath(fullpath)


if (__name__ == "__main__"):
    if len(args) == 3:
        h = HotelHTMLGenerator(args[1], args[2])
    else:
        h = HotelHTMLGenerator()
    print("\narguments: ", str(h.getArgs()), end="\n\n")
    ratesFilePath = h.scan()
    # h.generateHTML(ratesFilePath)
