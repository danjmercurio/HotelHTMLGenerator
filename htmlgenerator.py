#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@author Dan Mercurio <dmercurio92@gmail.com>
@date 8/14/2018
"""

# This has to come first because that's the rule
from __future__ import print_function  # Python 2/3 compatibility

# Standard library imports
from collections import OrderedDict, namedtuple
import os
import os.path
import sys
import textwrap
import datetime

# Third-party modules
import untangle
import termcolor
import dateutil.parser
import pprint


class HotelHTMLGenerator(object):
    """
    Singleton class to traverse a directory searching for a rates.input.xml file
    and for each directory containing this file, produce two HTML files
    (rate-chart.html and rate-month.html) with greater detail of
    the hotel rates across month intervals.
    """

    def __init__(self, search_directory="./test/search", output_directory="./test/output",
                 debug=True, year=2018):
        """ Constructor for the whole object. This is a singleton so there should only ever be one instance. """

        # First check if we are just displaying help text
        if ("-h" in sys.argv) or ("--help" in sys.argv):
            self.help()

        # Define constants
        self.string_constants = {
            "NEWLINE": "\n",
            "DOUBLE_NEWLINE": ("\n" * 2),
            r"TITLE_ASCII":
                r"""
  _   _       _       _ _   _ _____ __  __ _     ____                           _
 | | | | ___ | |_ ___| | | | |_   _|  \/  | |   / ___| ___ _ __   ___ _ __ __ _| |_ ___  _ __
 | |_| |/ _ \| __/ _ | | |_| | | | | |\/| | |  | |  _ / _ | '_ \ / _ | '__/ _` | __/ _ \| '__|
 |  _  | (_) | ||  __| |  _  | | | | |  | | |__| |_| |  __| | | |  __| | | (_| | || (_) | |
 |_| |_|\___/ \__\___|_|_| |_| |_| |_|  |_|_____\____|\___|_| |_|\___|_|  \__,_|\__\___/|_|

"""
        }

        # Fire things up.
        termcolor.cprint(
            self.string_constants["TITLE_ASCII"], color='cyan', on_color='on_grey')
        print("Reticulating splines...")

        # Load dependencies
        self.do_imports()

        # Debug mode attribute
        self.debug = debug

        if len(sys.argv) is 1 and not self.debug:
            print("Script was called with no arguments. If you need info, \
            invoke the script with -h or --help")
            raise SystemExit

        if self.debug:
            print("Debug mode ON.")

        # Output arguments script was called with if verbose was selected
        if self.debug:
            print("Arguments: ", str(sys.argv), end="\n\n")

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
        if "--year" in sys.argv:
            self.year = sys.argv[sys.argv.index("--year") + 1]
        else:
            self.year = year

        # Show the year in use
        print("Using year value of {0}".format(self.year))

        if "--relative" not in sys.argv:
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
        help_text = \
            """Usage: python[2.x|3.x] {0} [search directory] [output directory] [--arguments (optional)]
Pass --relative to disable conversion of relative paths to absolute paths. Pass
--year (4 digit year) to use a year other than 2018. Pass -h or --help to
print this message.""".format(sys.argv[0])
        print(help_text)
        raise SystemExit

    # noinspection PyPep8Naming
    def do_imports(self):
        # Third-party libraries
        try:
            import dateutil.parser as date_parser
        except ImportError as error:
            MISSING_DEPENDENCY = "".join(
                char for char in str(error).split(" ")[-1] if char.isalnum() or char in [",", " ", "."])
            # Create some space by printing newlines
            print(self.string_constants["DOUBLE_NEWLINE"])
            # This is fancy
            termcolor.cprint(
                "Fatal Error❗",
                color="red",
                on_color="on_grey",
                attrs=["bold", "underline", "blink"],
                sep=self.string_constants["NEWLINE"],
                end="\r\n")
            wrapper = textwrap.TextWrapper(
                initial_indent="",
                fix_sentence_endings=True,
                drop_whitespace=True)
            DEPENDENCY_ERRORMESSAGE = """A required Python module could not be found. The {0} module(s) for Python {1}.x must be installed using pip, easy_install, the system package manager (apt-get on Debian based Linux OSes, pacman on Arch and Arch-based distributions including Manjaro, or dnf in the case of Fedora. Consult your distribution's manual to learn how to properly install Python {1} modules. PIP is the easiest and best method, but in case of last resort you can download the source from the module's distributor and run its install script yourself.""".format(
                MISSING_DEPENDENCY, sys.version_info.major)
            print(wrapper.fill(DEPENDENCY_ERRORMESSAGE))
            raise SystemExit("Cannot continue. Halting...")

    @staticmethod
    def daterange(start_date, end_date):
        """ Helper function for iterating over dates. """
        if (start_date <= end_date):
            for n in range((end_date - start_date).days + 1):
                yield start_date + datetime.timedelta(n)
        else:
            for n in range((start_date - end_date).days + 1):
                yield start_date - datetime.timedelta(n)

    def getDirs(self):
        """ Get a hash of the directories we are using for search and output."""
        return self.dirs

    def printDirs(self):
        return "self.dirs updated to {0}".format(pprint.pprint(self.getDirs()))

    def setDirs(self, new_dirs):
        """ Setter for input/output directories. """
        try:

            # Ensure that candidate directories are a dictionary or OrderedDict
            assert isinstance(new_dirs, dict) or isinstance(
                new_dirs, OrderedDict)

            self.dirs['search_directory'] = new_dirs['search_directory']
            self.dirs['output_directory'] = new_dirs['output_directory']

            # Log new directories if debug mode is on
            if self.debug: self.printDirs()

            # Return new dirs
            return self.dirs
        except AssertionError:
            raise SystemExit("Attempted to set directories to a non-dictionary \
            object")
        except KeyError:
            raise SystemExit(
                "Attempted to set directories with a dictionary of \
            invalid keys. Required keys: 'search_directory', 'output_directory'.")

    def scan(self):
        """ Scan for input xml files and populate the paths attribute with
        results. Return self to support method chaining. """

        # Get the directory to start from
        search_directory = self.getDirs().get('search_directory')

        # Make sure it actually exists
        if not os.path.exists(search_directory):
            raise SystemExit("Specified search directory does not exist.")
        else:
            def search(search_directory):
                """ Generator which scans recursively for a rates.input.xml
                file and yields their paths """
                for root, _, files in os.walk(search_directory):

                    # Make the search case insensitive by converting everything to lower case
                    files = [current_file.lower() for current_file in files]

                    # Look for our XML file in among the files in the current directory
                    if self.SEARCH_FILENAME in files:
                        # Join path and filename
                        fullpath = os.path.join(root, self.SEARCH_FILENAME)

                        # Detect symlinks
                        try:
                            assert not os.path.islink(fullpath)
                        except AssertionError:
                            print("Search result is a symlink (shortcut). \
                            Will use real path instead.")
                            continue
                        fullpath = os.path.realpath(fullpath)

                        # Verify we are actually pointing toward a file
                        try:
                            assert os.path.isfile(fullpath)
                        except AssertionError:
                            print("OS reports search result at {0} not an actual file. Trying to continue...".format(
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
            raise SystemExit("No rates.input.xml files found in recursive search of {0}".format(
                self.getDirs().get('search_directory', 'requested directory.'))
            )

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
            raise SystemExit(
                "Unable to find detected XML file paths. Could be a typo.")

        # Get a list of all <date> tags from the XML
        date_tags = []

        for path in self.paths:
            with open(path, 'r') as xmlFileHandle:
                doc = untangle.parse(xmlFileHandle.read())

                self.parser_objects.append(doc)
                if self.debug:
                    print("Untangle parser #{0}".format(
                        str(len(self.parser_objects))), "repr:",
                        repr(self.parser_objects[(len(self.parser_objects) - 1)]))

        for xml_parser in self.parser_objects:
            print("Parsing hotel code {0}".format(xml_parser.hotel['code']))

            for room in xml_parser.hotel.room:
                room_description = room.description.cdata.strip()
                room_rates = room.rate
                print(room_description)
                for rate in room_rates:
                    for tag in rate.date:
                        date_tags.append(tag)

        if self.debug: print("{0} <date> tags processed".format(str(len(date_tags))))

        # Iterate over every day of the year. The year to use is a property of the top level object.

        start_date = datetime.date(self.year, 1, 1)
        end_date = datetime.date(self.year, 12, 31)

        # Use the generator self.daterange to get a list of days in a year
        days_in_year = [day for day in self.daterange(start_date, end_date)]

        # Sanity check: length of days_in_year should always be 365
        assert len(days_in_year) == 365

        # Make it a tuple with a list for each day
        days_in_year = zip(days_in_year, [[] for x in range(365)])
        added = 0
        for day in days_in_year:
            for date_tag in date_tags:
                tag_start_year, tag_start_month, tag_start_day = [int(item) for item in date_tag['start'].split('-')][0], [int(item) for item in date_tag['start'].split('-')][1], [int(item) for item in date_tag['start'].split('-')][2]
                tag_start = datetime.date(tag_start_year, tag_start_month, tag_start_day)

                tag_end_year, tag_end_month, tag_end_day = [int(item) for item in date_tag['end'].split('-')][0], [int(item) for item in date_tag['end'].split('-')][1], [int(item) for item in date_tag['end'].split('-')][2]
                tag_end = datetime.date(tag_end_year, tag_end_month, tag_end_day)

                # If the day of current iteration falls within the date range of the <date> XML tag, create a tuple to link them and append it to the days_tags_tuples list
                print("{0}, {1}, {2}".format(tag_start, day[0], tag_end))
                if (tag_start <= day[0] <= tag_end):
                    day[1].append(date_tag)
                    print("added")
                    added = added + 1

        print(days_in_year)
        print("Added: {0}".format(added))







        return self

    def generate_html(self):
        raise NotImplementedError

    def write_output(self):
        """ @input Rendered Jinja2 templates
            @output Written html files.
            @returns True on successful write or raises an exception for invalid input or I/O errors like no write permissions
        """
        output_files = ['rate_calendar', 'rates_yearly_summary']

        print("Writing to output files has not yet been implemented.")
        return self


if __name__ == "__main__":
    # Create an instance of our worker class
    if len(sys.argv) == 3:
        hg = HotelHTMLGenerator(sys.argv[1], sys.argv[2])
    else:
        hg = HotelHTMLGenerator("./test/search", "./test/output", debug=True)

    # Chain of actions this script is designed to perform
    hg.scan().parse().generate_html().write_output()
