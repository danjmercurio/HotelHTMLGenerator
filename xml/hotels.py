#!/usr/bin/python3.7

'''
Written for python 3.7 (current latest version) but I
have added some workarounds for python 2.x compatibility.
This requires beautifulsoup4, which I installed with pip,
and python3-toolz, which you can install with apt-get if you
are on Debian or some Debian respin. For python 2.x the package is
just python-toolz. Most importantly it requires the lxml XML parser,
installed the same way as the aforementioned toolz package.
'''

import bs4
from toolz import first, last
from os.path import exists
from os import getcwd
import sys

rates = open('./rates.xml', 'r')
soup = bs4.BeautifulSoup(markup=rates.read(), features="xml")
rates.close()
hotels = soup.find_all('hotel')
with open(sys.stdout, 'w') as stdout:
    stdout.write("Found {0} hotel tags".format(str(len(hotels))))
for hotel in enumerate(hotels):
	#hotelNum, hotelSoup = first(hotel), last(hotel))
	path = "./hotel_xml_files/hotel_{0}.xml".format(first(hotel))
	if not exists("./hotel_xml_files"): raise SystemExit("subfolder {0}/hotel_xml_files not found, nowhere to write to".format(getcwd()))
	with open(path, 'w') as output:
		output.write("<!-- begin hotel {0} -->\n".format(first(hotel)))
		outputString = last(hotel).prettify()
		output.write(outputString)
		output.write("<!-- end hotel {0} -->\n".format(first(hotel)))
