#!/usr/bin/python
from __future__ import print_function

class extendedList(list):
    
    def __init__(self, iterable):
        super().__init__(iterable)

    def foreach(self, callback):
        for item in self:
        	index = self.index(item)
        	self[index] = callback(item)

if (__name__ == '__main__'):
	l = [1, 2, 3]
	el = extendedList(l)
	el.foreach(lambda x: x + 1)
	print(el)
	# try:
	# #assert el.foreach(lambda x: x) == l
	# #
	# except AssertionError as ae:
	# 	print("Members of exception: ", dir(ae), end="\n")
