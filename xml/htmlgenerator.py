#!/usr/bin/python
# -*- coding: ascii -*-

from __future__ import print_function # Python 2/3 compatibility

"""
@author Dan Mercurio <dmercurio92@gmail.com>
@date 8/14/2018
"""

# Standard library imports
from os import walk, linesep
import os.path
import sys
from sys import argv as args, version_info
import pdb
from collections import OrderedDict
import sys
import os
import inspect
import json
from underscore import _

# Third-party libs
try:
    import yattag, bs4, lxml, dateutil.parser
except ImportError as ie:
    missing_dependency = "".join(char for char in ie.msg.split(" ")[-1] if char.isalnum())
    print("Fatal Error(LineException): a required Python module could not be found.",
    "The " + missing_dependency + " module for Python " + str(version_info.major) + ".x must be installed using pip, easy_install,",
    "the system package manager (apt-get on Debian based Linux OSes), " +
    "or manually downloading and extracting.", sep="\n", end="\n\nExiting...\n")
    raise SystemExit

''' Util functions '''

# def each(iterable, callback):
#     """ My own humble convenience function for functional iteration. """
#     for index, item in enumerate(iterable):
#         callback(iterable, index, item)
#         # ex. lambda x,y,z: x[y] -> z

def lineno():
    """ Returns the current line number of execution. """
    line = inspect.currentframe().f_back.f_lineno
    line = str(line)
    return line

# def print_with_line(args, end):
#    ''' Causing problems with end argument '''
#     default_print(lineno(), args)
#print = print_with_line

class LineException(BaseException):
    def __init__(self):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

Exception = LineException

def prettyprint(d):
    ''' Convert dictionaries to JSON and print human-readable format. '''
    if isinstance(d, str):
        print(d, end="\nWARNING: Type prettyprinted above was string, expected dictionary.\n")
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
      import traceback, pdb
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

    def __init__(self, search_directory = "./search", output_directory = "./output", year = "2018", debug = True):
        """ Initialization of new instance. """

        # First check if we are just displaying help text
        if ("-h" in args) or ("--help" in args):
            self.help()

        if len(args) is 1:
            print("Script was called with no arguments. If you need info, invoke the script with -h or --help")
            raise SystemExit

        # Debug mode attribute
        self.debug = debug

        # Output arguments script was called with if verbose was selected
        if self.debug: print("Arguments: ", str(self.getArgs()), end="\n\n")


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

    def setDirs(self, new_dirs):
        """ Setter for input/output directories. """
        if self.debug:
            if not bool(self.getDirs()):
                print("Initializing search and output directories for the first time.")
            else:
                print("Requested to change these self.dirs values: {0}\n".format(self.getDirs()))
        try:
            assert isinstance(new_dirs, dict) or isinstance(new_dirs, OrderedDict) # Check that candidate dirs are a dictionary hash
            try:
                assert (len(new_dirs.keys()) >= 2) # Additional validation for candidate dirs
                self.dirs['search_directory'] = new_dirs['search_directory']
                self.dirs['output_directory'] = new_dirs['output_directory']

                if self.debug: print("self.dirs updated to {0}\n".format(self.dirs))

                # Return new dirs
                return self.dirs
            except AssertionError:
                lineno()
                raise SystemExit("Attempted to set directories with a dictionary missing keys")

        except AssertionError:
            raise SystemExit("Attempted to set directories to a non-dictionary object")
        except KeyError:
            raise SystemExit("Attempted to set directories with a dictionary of invalid keys. Required keys: 'search_directory', 'output_directory'.")

    @staticmethod
    def getArgs():
        """ Get an enumerated list comprehension of the arguments with which the program was called. """
        return [arg for arg in enumerate(args)]

    def scan(self):
        """ Scan for input xml files and populate the paths attribute with results.
        return self to support method j """

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
        search_results = search(search_directory)
        for result in search_results:
            self.paths.append(result)

        # Output found paths if verbose mode was selected
        if self.debug: print("Paths found by search: ", self.paths)

        return self

    def parse(self):
        """ @input: XML file paths attribute populated by scan() earlier in the method chain.
            @output: Populate top level object HotelHTMLGenerator.parser_objects attribute with XML parsers for each file loaded with the element tree from the hotel elements down
            @returns self to support further method chaining.
        """
        for xmlfile in self.paths:
            if not os.path.exists(xmlfile) or not os.path.isfile(xmlfile):
                raise SystemExit("Generate HTML function was called with an invalid path or file.")
            try:
                with open(xmlfile) as file:
                # Entering file context

                    # Parse raw XML
                    hotels = bs4.BeautifulSoup(file.read(), "lxml").find_all('hotel')

                    try:
                        # Make sure the main XML document was parsed correctly and <hotel> tags were found.
                        assert len(hotels) is not 0

                        # This attribute is mainly for introspection of the XML to be parsed, hence its being stored prettified.
                        if self.debug: self.xml_strings = [hotel.prettify() for hotel in hotels]



                        # Parser objects that the generate_html method will use.
                        for hotel_parser_object in hotels:
                            try:
                                hotelCode = hotel_parser_object.get('code')
                                assert (isinstance(hotelCode, str) or isinstance(hotelCode, unicode))
                                assert len(hotelCode) > 1
                            except AssertionError as ae:
                                raise SystemExit('Unable to determine hotel code from <hotel> tag in rates file {0}'.format(file.name))

                        # Make a tuple
                        hotelTuple = (hotelCode, hotel_parser_object)

                        # Append to main object
                        self.parser_objects.append(hotelTuple)
                    except AssertionError:
                        raise SystemExit('No <hotel> tags found')
            except IOError(LineException):
                raise SystemExit("Unable to read found XML file.")
            # Leaving file context, file handler closed
        if self.debug:
            print("Hotels parsed: {0}".format(str(len(hotels))))

            for po in self.parser_objects:
                assert isinstance(po[1], bs4.element.Tag)
                print("self.parser_objects: ", "Hotel: {0}".format(po[0]), "Parser(type:{0}): {1}".format(type(po[1]), po[1].prettify()[100:150]), sep="\n---------\n", end="\n ------ end parser objects-----\n" )
        return self

    def generate_html(self):
        ''' @input XML parsers stored as attribute on top level object
            @output for each expected output file, a tuple with the path where the file will be written, and the HTML to be written as a string. ex: [(output/high_low_rates.html, '<html>...</html>'), (output/blah.html), <html>...</html>), ...] appended to the top level object's html_strings attribute
            @returns self to support method chaining
        '''

        # An OrderedDict to hold lists of rates and the month to which they apply. Keys are month numbers.
        months = range(1, 13)
        months_and_rates = OrderedDict(map(lambda month: (month, []), months))
        # -> {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], ... }

        # Here we define the callback for xml to html translation
        def html_from_xml(hotel):
            # Hotel is the top level element. A hotel has many rooms.
            hotelCode = hotel.get('code')
            rooms = hotel.findChildren('room')
            if len(rooms) is 0:
                raise SystemExit('Encountered a hotel with no rooms. XML document may be incomplete or malformed.')
            else:
                # Each room has a name attribute and a human readable <description> which is a verbose name
                # Initialize a dict to store this and its child tags, <rate>, where we get rate dates and prices
                rooms_list = []
                for room in rooms:
                    room_hash = OrderedDict()
                    room_hash['name'] = room.get('name')
                    room_hash['description'] = room.findChildren('description')[0].string.strip()
                    dates = room.findChildren('date')
                    for date in dates:
                        date_hash = room_hash['dates'] = OrderedDict()
                        start = room_hash['dates']['start'] = date.get('start')
                        end = room_hash['dates']['end'] = date.get('end')
                        #print("date > room_price: ", date.findChildren('room_price'))
                        room_prices = date.findChildren('room_price')
                        if (len(room_prices) is 1):
                            price = room_hash['dates']['price'] = float(date.findChildren('room_price')[0].string.strip())
                        else:
                            price = room_hash['dates']['price'] = float(0) # No price detected in XML


                        # Calculate if start/end is within 1 month
                        start_datetime = dateutil.parser.parse(start)
                        end_datetime = dateutil.parser.parse(end)

                        if (start_datetime.month == end_datetime.month) and (start_datetime.year == end_datetime.year) and (start_datetime.day < end_datetime.day):
                            # This interval is within one month and does not cross a month boundary,
                            # and it is not a case where month comparison is true but the months are of
                            # completely different years, because the year must be equal as well.
                            # The day value comparison is a final sanity check. If start day is less than
                            # end day, we must be moving forward in time within one month
                            months_and_rates.get(start_datetime.month).append(price)
                        else:
                            if self.debug:
                                print("Invalid datetime: ", start_datetime.__str__(), end_datetime.__str(), "Skipped...")

                        pdb.set_trace()


                        # Get min/max rates for that month
                    rooms_list.append(room_hash)

            # Filter out only the highest and lowest rates for each month
            for month, ratesList in months_and_rates.items():
                if len(ratesList) is 0:
                    ratesList.append(0)
                minmax = {
                    'lowest': min(ratesList),
                    'highest': max(ratesList)
                    }

                months_and_rates[month] = minmax

            print("Hotel: {0}".format(hotelCode))
            print("Min/max rates by month:")
            prettyprint(months_and_rates)
            print("Room info:")
            for room in rooms_list:
                prettyprint(room)

            generated_tuple = (hotelCode, "".join(months_and_rates[0:100], "...cont'd"), "".join(rooms_list[0:100], "...cont'd"))

            return (hotelCode, months_and_rates, rooms_list)

        with open('parser_objects.txt', 'a') as pobj:
            for index, item in enumerate(self.html_strings):
                print("self.parser_objects: ", "Hotel: {0}".format(po[0]), "Parser({0}): {1}".format(type(po[1]), po[1].prettify()), sep="\n---------\n", end="\n ------ end parser objects-----\n", file=pobj)

        return self

    def write_output(self):
        """ @input Write the generated HTML stored in the attributes of the singleton class instance to their respective files.
            @output Written html files.
            @returns True on successful write or raises an exception for invalid input or I/O errors like no write permissions
        """
        print("Writing to output files has not yet been implemented.")
        return self

if (__name__ == "__main__"):

    # Create an instance of our worker class
    if len(args) == 3:
        hg = HotelHTMLGenerator(args[1], args[2])
    else:
        hg = HotelHTMLGenerator()

    # Chain of actions this script is designed to perform
    hg.scan().parse().generate_html().write_output()
