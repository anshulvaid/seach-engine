#!/usr/bin/python
import re
import sys

# class Token:

# 	def __init__(self, value):
# 		self.val = value

def tokenize(TextFilePath):
	tokenList = []
	with open(TextFilePath) as fi:
		for line in fi:
			words = filter(None,re.split("\W+|_", line))
			tokenList += words
			# for word in words:
			# 	token = Token(word)
			# 	tokenList.append(token)
	return tokenList

def computeWordFrequencies(TokenList):
	freq = {}
	for token in TokenList:
		lower = token.lower()
		if lower in freq:
			freq[lower] += 1
		else:
		 	freq[lower] = 1
	return freq


def printF(Frequencies):
	for k,v in sorted(Frequencies.items(), key=lambda t:(t[1],t[0]), reverse=True):
		print("{0}, {1}".format(k,v))

def main(argv):
	if len(argv) < 2:
		print("Please enter the file name.")
	else:
		tokens = tokenize(argv[1])
		freq = computeWordFrequencies(tokens)
		printF(freq)

if __name__ == "__main__":
	main(sys.argv)
	