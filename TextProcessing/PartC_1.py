#!/usr/bin/python
import re
import sys

def union(filepath1, filepath2):
	result = {}
	with open(filepath1) as fi1:
		with open(filepath2) as fi2:
			word1 = fi1.readline()
			word2 = fi2.readline()
			while True:	
				if not word1 or not word2:
					break
				count1 = (re.split('\W+', word1.strip('\n')))[1]
				word1 = word1[0]
				count2 = (re.split('\W+', word2.strip('\n')))[1]
				word2 = word2[0]
				if word1 < word2:
					result[word1] = int(count1)
					word1 = fi1.readline()
				elif word2 < word1:
					result[word2] = int(count2)
					word2 = fi2.readline()
				else:
					result[word1] = int(count1) + int(count2)
					word1 = fi1.readline()
					word2 = fi2.readline()
			while word1:
				result[word1] = int(count1)
				word1 = fi1.readline()
				if not word1:
					break
				count1 = (re.split('\W+', word1.strip('\n')))[1]
				word1 = word1[0]
			while word2:
				result[word2] = int(count2)
				word2 = fi2.readline()
				if not word2:
					break
				count2 = (re.split('\W+', word2.strip('\n')))[1]
				word2 = word2[0]

	return result


def printF(Frequencies):
	for k,v in sorted(Frequencies.items(), key=lambda t:t[0]):
		print("{0}, {1}".format(k,v))

def main(argv):
	if len(argv) < 3:
		print("Please enter the file names.")
	else:
		freq = union(argv[1], argv[2])
		printF(freq)

if __name__ == "__main__":
	main(sys.argv)
