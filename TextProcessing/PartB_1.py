#!/usr/bin/python
import re
import sys
import os

def intersect(filepath1, filepath2):
	if os.path.getsize(filepath1) > os.path.getsize(filepath2):
		temp = filepath1
		filepath1 = filepath2
		filepath2 = temp
	uni_items = set()
	result = set()
	count = 0
	with open(filepath1) as fi:
		for line in fi:
			words = filter(None,re.split("\W+|_", line))
			for word in words:
				uni_items.add(word.lower())
	with open(filepath2) as fi:
		for line in fi:
			words = filter(None,re.split("\W+|_", line))
			for word in words:
				if word.lower() in uni_items:
					result.add(word.lower())
	print(result)
	return len(result)

def main(argv):
	if len(argv) < 3:
		print("Please enter the file names.")
	else:
		count = intersect(argv[1], argv[2])
		print (count)
if __name__ == "__main__":
	main(sys.argv)
