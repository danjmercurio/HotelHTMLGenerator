#!/usr/bin/python3.7
import bs4
from toolz import first, last
from os.path import exists

rates = open('./rates.xml', 'r')
soup = bs4.BeautifulSoup(markup=rates.read(), features="xml")
rates.close()
hotels = soup.find_all('hotel')
for hotel in enumerate(hotels):
	#hotelNum, hotelSoup = first(hotel), last(hotel))
	path = "./hotel_xml_files/hotel_{0}.xml".format(first(hotel))
	if not exists("./hotel_xml_files"): raise SystemExit("subfolder (current dir)/hotel_xml_files not found, nowhere to write to")
	with open(path, 'w') as output:
		output.write("<!-- begin hotel {0} -->\n".format(first(hotel)))
		outputString = last(hotel).prettify()
		output.write(outputString)
		output.write("<!-- end hotel {0} -->\n".format(first(hotel)))
