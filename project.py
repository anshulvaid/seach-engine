#!/usr/bin/python
import re

class Token:

	def __init__(self, value):
		self.val = value

def tokenize(TextFilePath):
	tokenList = []
	with open(TextFilePath) as fi:
		for line in fi:
			words = filter(None,re.findall("[\w'-]+", line))
			for word in words:
				token = Token(word)
				tokenList.append(token)
	return tokenList


