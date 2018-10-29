#!/usr/lib/python3

'''
general tests for the HotelHTMLGenerator class
'''
import sys
sys.path.append("/home/dan/PycharmProjects/lantera/xml")
import xml.HotelHTMLGenerator

DEFAULT_ARGS = ['./test/search', './output']



def help_exception_test():
    failed = False
    try:
        # Add --help to sys.argv to simulate being called with help
        sys.argv.append("--help")
        testHTG = HotelHTMLGenerator(' '.join(DEFAULT_ARGS)) # Space is important in ' '
    except:
        failed = True
    return not failed




if __name__ == '__main__':
    tests = {
        'Name': 'Help function does not raise any exceptions.',
        'func': help_exception_test
    }

    for testName, test in tests.items():
        print("Running test: {0}".format(testName))
        if test():
            print("Test passed.")
        else:
            raise SystemExit("Test " + testName + " failed!")