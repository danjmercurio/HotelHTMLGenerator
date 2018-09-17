#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function # Python 2/3 compatibility

"""
@author Dan Mercurio <dmercurio92@gmail.com>
@date 8/14/2018
"""

# Standard library imports
from os import walk, linesep
import os.path
from sys import argv as args, version_info

# Third-party libs
try:
    import yattag, bs4, lxml
except ImportError as ie:
    missing_dependency = "".join(char for char in ie.msg.split(" ")[-1] if char.isalnum())
    print("Fatal error: a required Python module could not be found.",
    "The " + missing_dependency + " module for Python " + str(version_info.major) + ".x must be installed using pip, easy_install,",
    "the system package manager (apt-get on Debian based Linux OSes), " +
    "or manually downloading and extracting.", sep="\n", end="\n\nExiting...\n")
    raise SystemExit


def each(iterable, callback):
    """ My own humble convenience function for functional iteration. """
    for index, item in enumerate(iterable):
        callback(iterable, index, item)
        # ex. lambda x,y,z: x[y] -> z


class HotelHTMLGenerator(object):
    """
    Singleton class to traverse a directory searching for a rates.input.xml file
    and for each directory containing this file, produce two HTML files
    (rate-chart.html and rate-month.html) with greater detail of
    the hotel rates across month intervals.
    """

    def __init__(self, search_directory = "./search", output_directory = "./output", year = "2018"):
        """ Initialization of new instance. """

        # First check if we are just displaying help text
        if ("-h" in args) or ("--help" in args):
            self.help()

        if len(args) is 1:
            print("Script was called with no arguments. If you need info, invoke the script with -h or --help")
            raise SystemExit

        # Attribute that stores search and output directories as a dict
        self.dirs = dict()

        # Populate the attribute upon initialization
        self.setDirs({
            'search_directory': search_directory,
            'output_directory': output_directory
        })

        self.SEARCH_FILENAME = 'rates.input.xml'  # Constant for our search file

        # Set the year to 2018 AD unless otherwise
        # specified in the arguments
        if "--year" in args:
            self.year = args[args.index("--year") + 1]
        else:
            self.year = year

        if "--relative" not in args:
            absolute_dirs = [os.path.realpath(val) for val in self.getDirs().values()]
            joined_keys_and_vals = zip(self.getDirs().keys(), absolute_dirs)
            joined_keys_and_vals = dict(joined_keys_and_vals)
            self.setDirs(joined_keys_and_vals)

        # An attribute to hold the paths to discovered search results
        self.paths = list()

        # An attribute to hold the XML parser objects
        self.parser_objects = list()

        # An attribute to hold prettified raw XML strings for inspection/introspection
        self.xml_strings = list()

        # An attribute to hold generated html in string form for writing to files
        self.html_strings = list()

    @staticmethod
    def help():
        """ Print the help text. """
        helpText = """Usage: python[3] {0} [search directory] [output directory] [--arguments (optional)]{1}
Pass --relative to disable conversion of relative paths to absolute paths. Pass --year (4 digit year) to use a year other than 2018. Pass -h or --help to print this message""".format(args[0], linesep)
        print(helpText)
        raise SystemExit

    def getDirs(self):
        """ Get a hash of the directories we are using for search and output. """
        return self.dirs

    def setDirs(self, dirs):
        """ Setter for input/output directories. """
        try:
            assert isinstance(dirs, dict)
            try:
                assert (len(dirs.keys()) == 2)
                self.dirs['search_directory'] = dirs['search_directory']
                self.dirs['output_directory'] = dirs['output_directory']
                return self.dirs
            except AssertionError:
                raise SystemExit("Attempted to set directories with a dictionary missing keys")
        except AssertionError:
            raise SystemExit("Attempted to set directories to a non-dictionary object")

        except KeyError:
            raise SystemExit("Attempted to set directories with a dictionary of invalid keys")

    @staticmethod
    def getArgs():
        """ Get an enumerated list comprehension of the arguments with which the program was called. """
        return [arg for arg in enumerate(args)]

    def __getattr__(self, item):
        pass

    def __getitem__(self, item):
        pass

    def scan(self):
        """ Scan for input xml files and populate the paths attribute with results """

        # Get the directory to start from
        search_directory = self.getDirs().get('search_directory')

        # Make sure it actually exists
        if not os.path.exists(search_directory):
            raise SystemExit("Specified search directory does not exist.")
        else:
            def search(search_directory):
                """ Generator which scans recursively for a rates.input.xml file and yields their paths """
                for root, dirs, files in walk(search_directory):

                    # Make the search case insensitive by converting everything to lower case
                    files = [file.lower() for file in files]

                    # Look for our XML file in among the files in the current directory
                    if self.SEARCH_FILENAME in files:

                        # Join path and filename
                        fullpath = os.path.join(root, self.SEARCH_FILENAME)

                        # Detect symlinks
                        try:
                            assert not os.path.islink(fullpath)
                        except AssertionError as e:
                            print("Search result is a symlink (shortcut). Will use real path instead.")
                            continue
                        fullpath = os.path.realpath(fullpath)


                        # Verify we are actually pointing toward a file
                        try:
                            assert os.path.isfile(fullpath)
                        except AssertionError:
                            print("OS reports search result at {0} is not an actual file. Trying to continue...".format(fullpath))
                            continue

                        # Try to convert a relative path to an absolute path
                        fullpath = os.path.realpath(fullpath)

                        # Report result
                        print("Found {0} at {1}".format(self.SEARCH_FILENAME, fullpath))

                        yield fullpath

        each(search(search_directory), lambda iterable, index, item: self.paths.append(item))

        return self

    def parse(self):
        """ Parse XML files at each found path. Generate HTML from each parser object, and output it"""
        for xmlfile in self.paths:
            if not os.path.exists(xmlfile) or not os.path.isfile(xmlfile):
                raise SystemExit("Generate HTML function was called with an invalid path or file.")
            try:
                with open(xmlfile) as file: # Entering file context

                    # Read from file
                    contents = file.read()

                    # Parse raw XML
                    hotels = bs4.BeautifulSoup(contents, "lxml").find_all('hotel')

                    try:
                        assert len(hotels) is not 0


                        self.xml_strings = [hotel.prettify() for hotel in hotels]

                        self.parser_objects = [hotel for hotel in hotels]

                    except AssertionError:
                        raise SystemExit('No <hotel> tags found')
            except IOError:
                raise SystemExit("Unable to read found XML file.")
            # Leaving file context, file handler closed
        return self

    def generate_html(self):
        # Here we define the callback for xml to html translation
        def html_from_xml(xml_string):
            print(xml_string)
            pass

        # Generate html
        html_strings = each(self.parser_objects, lambda x, y, z: html_from_xml(z))
        each(html_strings, lambda x, y, z: self.html_strings.append(z))

        # Append each html string to the main object's attribute
        each(html_strings, lambda iterable, index, item: self.html_strings.append(item))

        return self

    def write_output(self):
        """ Write the generated HTML stored in the attributes of the singleton class instance to their respective files."""
        return self

if (__name__ == "__main__"):
    # Create an instance of our worker class
    if len(args) == 3:
        hg = HotelHTMLGenerator(args[1], args[2])
    else:
        hg = HotelHTMLGenerator()
    # print("arguments: ", str(hg.getArgs()), end="\n\n")
    # print("paths: ", [x for x in hg.scan()], end="\n\n")

    # Chain of actions this script is designed to perform
    hg.scan().parse().generate_html().write_output()
