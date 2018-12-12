# HotelHTMLGenerator
A Python 2.x-based script I wrote for a client with a very specific requirement. 
This script scans a given directory (by default *./test/search/*) recursively for an XML file
containing data that specifies the rates and the rooms and dates to which those rates apply
for a chain of luxury hotels. Then it parses the XML with the wonderful **untangle** library and exports
two purpose-built HTML files: one containing a summary of high and low rates for each month, and another containing an 
interactive calendar showing the rates for each day.

There is also a suite of unit tests designed to be used with the **pytest** module.

`This script remains a work in process.`