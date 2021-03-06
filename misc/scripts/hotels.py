#!/usr/bin/python

'''
THIS DOES NOT NEED TO BE RUN BY THE END USER BUT HAS BEEN INCLUDED IN THE REPOSITORY
LEST IT BE LOST TO THE SANDS OF TIME

Splits each <hotel> tag in rates.xml and its descendents into
separate XML files for further parsing and manipulation.
Written for python 3.7 (current latest version) but I
have added some workarounds for python 2.x compatibility.
This requires beautifulsoup4, which I installed with pip,
and python3-toolz, which you can install with apt-get if you
are on Debian or some Debian respin. For python 2.x the package is
just python-toolz. Most importantly it requires the lxml XML parser,
installed the same way as the aforementioned toolz package.
'''

import sys
from os import getcwd
from os.path import exists

import bs4
from toolz import first, last

print("THIS DOES NOT NEED TO BE RUN BY THE END USER BUT HAS BEEN INCLUDED IN THE REPOSITORY \
LEST IT BE LOST TO THE SANDS OF TIME. Only run if you know what you are doing.")

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
with open("./hotel_xml_files/README.txt", 'w') as readme:
    readme.write("These files were generated by the hotels.py script in the directory above. This was done to make handling each hotel XML tree much more managable on slower systems by splitting the original 18MB rates.xml file by each individual hotel tag. It was also necessary to format the individual <hotel> nodes specifically by properly indenting the child tags to make the still-large XML files much more readable for humans and thereby expedite development time. Two test hotel XML trees in particular were selected and moved to the parent directory, AAAAAA.xml and HNLADR.xml. hotels.py is a convenience script to aid in the process of developing the main script and will not be updated heretofore. ".replace(". ", "\n"))
