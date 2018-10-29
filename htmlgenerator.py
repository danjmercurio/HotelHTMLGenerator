#!/usr/bin/python3
# -*- coding: utf-8 -*-

# This has to come first because that's the rule
from __future__ import print_function  # Python 2/3 compatibility
# Standard library imports
import json
import os
import os.path
import pdb
import sys
import termcolor
from collections import OrderedDict
from inspect import currentframe
import textwrap
"""
@author Dan Mercurio <dmercurio92@gmail.com>
@date 8/14/2018
"""

# Some constants
ARGS = sys.argv
NEWLINE = "\n"
DOUBLE_NEWLINE = NEWLINE * 2
TITLE_ASCII = \
"""
  _   _       _       _ _   _ _____ __  __ _     ____                           _
 | | | | ___ | |_ ___| | | | |_   _|  \/  | |   / ___| ___ _ __   ___ _ __ __ _| |_ ___  _ __
 | |_| |/ _ \| __/ _ | | |_| | | | | |\/| | |  | |  _ / _ | '_ \ / _ | '__/ _` | __/ _ \| '__|
 |  _  | (_) | ||  __| |  _  | | | | |  | | |__| |_| |  __| | | |  __| | | (_| | || (_) | |
 |_| |_|\___/ \__\___|_|_| |_| |_| |_|  |_|_____\____|\___|_| |_|\___|_|  \__,_|\__\___/|_|

"""
""" Util functions """


def lineno(datatype='string'):
    """ Returns the current line number of execution. """
    line = currentframe().f_back.f_lineno
    if datatype is not 'string':
        line = str(line)
    return line


# def print(*ARGS, **kwARGS):
#     frameinfo = currentframe()

#     try:
#         import __builtin__
#         __builtin__.print(frameinfo.f_back.f_lineno, ": ", sep='', end='')
#         return __builtin__.print(*ARGS, **kwARGS)
#     except NameError:
#         from builtins import print as _builtin_print
#         _builtin_print(frameinfo.f_back.f_lineno, ": ", sep='', end='')
#         return _builtin_print(*ARGS, **kwARGS)


class LineException(Exception):
    def __init__(self):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("-------------- Exception information: ----------------",
                    exc_type, fname, exc_tb.tb_lineno)


Exception = LineException


def prettyprint(d):
    ''' Convert dictionaries to JSON and print human-readable format. '''
    if isinstance(d, str):
        print(
            d,
            end="\nWARNING: Type prettyprinted above was string, expected \
        dictionary.\n")
        return
    if isinstance(d, dict) or isinstance(d, OrderedDict):
        print(json.dumps(d, sort_keys=True, indent=4))
    else:
        print("Argument to prettyprint() was not of type dict or OrderedDict.")


def info(type, value, tb):
    ''' Enter debugger on unhandled exceptions '''
    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
        # We are in interactive mode or we don't have a tty-like
        # device, so we call the default hook
        sys.__excepthook__(type, value, tb)
    else:
        import traceback
        import pdb
        # We are NOT in interactive mode, print the exception...
        traceback.print_exception(type, value, tb)
        print
        # ...then start the debugger in post-mortem mode.
        pdb.pm()


sys.excepthook = info
''' End utils '''


class HotelHTMLGenerator(object):
    """
    Singleton class to traverse a directory searching for a rates.input.xml file
    and for each directory containing this file, produce two HTML files
    (rate-chart.html and rate-month.html) with greater detail of
    the hotel rates across month intervals.
    """

    def __init__(self, search_directory="./search", output_directory="./output",
                debug=True, year=2018):
        """ Constructor for the whole object. This is a singleton so there should only ever be one instance. """

        # First check if we are just displaying help text
        if ("-h" in ARGS) or ("--help" in ARGS):
            self.help()

        # Fire things up.
        termcolor.cprint(TITLE_ASCII, color='cyan', on_color='on_grey')
        print("Reticulating splines...")
        self.doImports()

        # Debug mode attribute
        self.debug = debug

        if len(ARGS) is 1 and not self.debug:
            print("Script was called with no arguments. If you need info, \
            invoke the script with -h or --help")
            raise SystemExit

        if self.debug:
            print("Debug mode ON.")

        # Output arguments script was called with if verbose was selected
        if self.debug:
            print("Arguments: ", str(self.getARGS()), end="\n\n")

        # Initialize memory spade for an object attribute that stores search and output directories as a dict and initialize them with their default values
        self.dirs = dict({
            'search_directory': None,
            'output_directory': None
        })

        # Populate the attribute upon initialization
        self.setDirs({
            'search_directory': search_directory,
            'output_directory': output_directory
        })

        self.SEARCH_FILENAME = 'rates.input.xml'  # Constant for our search file

        # Set the year to 2018 AD unless otherwise
        # specified in the arguments
        if "--year" in ARGS:
            self.year = ARGS[ARGS.index("--year") + 1]
        else:
            self.year = year

        if "--relative" not in ARGS:
            absolute_dirs = [
                os.path.realpath(val) for val in self.getDirs().values()
            ]
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
        helpText = """Usage: python[3] {0} [search directory] [output directory\
        ] [--arguments (optional)]{1}
Pass --relative to disable conversion of relative paths to absolute paths. Pass\
 --year (4 digit year) to use a year other than 2018. Pass -h or --help to \
 print this message""".format(ARGS[0], os.linesep)
        print(helpText)
        raise SystemExit

    def doImports(self):
        try:
            import __builtin__
        except ImportError:
            # Python 3
            import builtins as __builtin__

        # Third-party libraries
        try:
            import untangle
            import dateutil.parser
        except ImportError as error:
            MISSING_DEPENDENCY = "".join(
                char for char in str(error).split(" ")[-1] if char.isalnum() or char in [",", " ", "."])
            # Create some space by printing newlines
            print(DOUBLE_NEWLINE)
            # This is fancy
            termcolor.cprint(
                "Fatal Error❗",
                color="red",
                on_color="on_grey",
                attrs=["bold", "underline", "blink"],
                sep=NEWLINE,
                end="\r\n")
            wrapper = textwrap.TextWrapper(
                initial_indent="",
                fix_sentence_endings=True,
                drop_whitespace=True)
            DEPENDENCY_ERRORMESSAGE = """A required Python module could not be found. The {0} module(s) for Python {1}.x must be installed using pip, easy_install, the system package manager (apt-get on Debian based Linux OSes, pacman on Arch and Arch-based distributions including Manjaro, or dnf in the case of Fedora. Consult your distribution's manual to learn how to properly install Python {1} modules. PIP is the easiest and best method, but in case of last resort you can download the source from the module's distributor and run its install script yourself.""".format(
                MISSING_DEPENDENCY, sys.version_info.major)
            print(wrapper.fill(DEPENDENCY_ERRORMESSAGE))
            raise SystemExit("Cannot continue. Halting...")

    def getDirs(self):
        """ Get a hash of the directories we are using for search and output."""
        return self.dirs

    def setDirs(self, new_dirs):
        """ Setter for input/output directories. """
        # if self.debug:
        #     # Avoid printing this message every time the object is instantiated
        #     if self.dirs is not {} and len(self.dirs) is not 0:
        #         print(
        #             "Requested to change these self.dirs values: {0}\n".format(
        #                 self.getDirs()))
        try:
            # Check that candidate dirs are a dictionary hash
            assert isinstance(new_dirs, dict) or isinstance(
                new_dirs, OrderedDict)
            try:
                self.dirs['search_directory'] = new_dirs['search_directory']
                self.dirs['output_directory'] = new_dirs['output_directory']

                if self.debug:
                    print("self.dirs updated to {0}\n".format(self.dirs))

                # Return new dirs
                return self.dirs
            except AssertionError:
                lineno()
                raise SystemExit("Attempted to set directories with a \
                dictionary missing keys")

        except AssertionError:
            raise SystemExit("Attempted to set directories to a non-dictionary\
            object")
        except KeyError:
            raise SystemExit(
                "Attempted to set directories with a dictionary of\
            invalid keys. Required keys: 'search_directory', 'output_directory'."
            )

    @staticmethod
    def getARGS():
        """ Get an enumerated list comprehension of the arguments with which \
        the program was called. """
        return [arg for arg in enumerate(ARGS)]

    def scan(self):
        """ Scan for input xml files and populate the paths attribute with \
        results.
        return self to support method joining """

        # Get the directory to start from
        search_directory = self.getDirs().get('search_directory')

        # Make sure it actually exists
        if not os.path.exists(search_directory):
            raise SystemExit("Specified search directory does not exist.")
        else:
            def search(search_directory):
                """ Generator which scans recursively for a rates.input.xml
                file and yields their paths """
                for root, dirs, files in os.walk(search_directory):

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
                            print("Search result is a symlink (shortcut). \
                            Will use real path instead.")
                            continue
                        fullpath = os.path.realpath(fullpath)

                        # Verify we are actually pointing toward a file
                        try:
                            assert os.path.isfile(fullpath)
                        except AssertionError:
                            print("OS reports search result at {0} not an \
                            actual file. Trying to continue...".format(
                                fullpath))
                            continue

                        # Try to convert a relative path to an absolute path
                        fullpath = os.path.realpath(fullpath)

                        # Report result
                        print("Found XML file {0} at {1}".format(
                            self.SEARCH_FILENAME, fullpath))

                        yield fullpath

        search_results = search(search_directory)

        for result in search_results:
            self.paths.append(result)


        if len(self.paths) is 0:
            raise SystemExit("No rates.input.xml files found in recursive search of {0}".format(self.getDirs().get('search_directory', 'requested directory.')))


        # Output found paths if verbose mode was selected
        if self.debug:
            print("Paths found by search: ", self.paths)

        return self

    def parse(self):
        """ @input: XML file paths attribute populated by scan() earlier
        in the method chain.
        @output for each expected output file, a tuple with the path where
            the file will be written, and the HTML to be written as a string.
            ex: [(output/high_low_rates.html, '<html>...</html>'),
            (output/blah.html), <html>...</html>), ...] appended to the top
            level object's html_strings attribute
        @returns self to support method chaining

             Rate calendar:
                1. needs JS in its template to support clickable popup
                2. Generate a table with the right number of days for each month
                3. Each cell is clickable and stores info
                4. Needs the following local variables:
                    Hash of calendar months and numbers of days in each
                    Get a rate from XML for each day
                    Need to use dateutil to verify rate applies to correct day
                    of month

            Rate summary:
                1. Needs the following local variables:
                    current year or year in top level object attribute self.year
                    List of rooms. For each room...
                    Room code
                    Room description (a longer string)
                    A hash with:
                        keys: months as words or their abbreviations
                        values: [minimum nightly rate, maximum nightly rate]

        After populating templates with data, call render on them and store as
        strings
            @returns self to support further method chaining.
        """

        # self.paths is the discovered xml file paths from .search
        # self.parser_objects is a list of instantiated parsers from paths
        # both are @props of top level object


        if len(self.paths) is 0:
            raise SystemExit('Unable to find detected XML file paths. Could be a typo.')

        def untangling():
            for path in self.paths:
                with open(path, 'r') as xmlFileHandle:
                    parser = untangle.parse(xmlFileHandle.read())

                    self.parser_objects.append(parser)



        return self


    def generate_html(self):


        return self

    def write_output(self):
        """ @input Rendered Jinja2 templates
            @output Written html files.
            @returns True on successful write or raises an exception for invalid input or I/O errors like no write permissions
        """
        output_files = ['rate_calendar', 'rates_yearly_summary']

        print("Writing to output files has not yet been implemented.")
        return self


if (__name__ == "__main__"):
    # Create an instance of our worker class
    if len(ARGS) == 3:
        hg = HotelHTMLGenerator(ARGS[1], ARGS[2])
    else:
        hg = HotelHTMLGenerator("./test/search", "./test/output", debug=True)

    # Chain of actions this script is designed to perform
    hg.scan().parse().generate_html().write_output()
