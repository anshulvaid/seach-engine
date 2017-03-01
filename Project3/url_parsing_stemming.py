from __future__ import division
import urllib2
import os
import re
import json
import math
import time
from Index import Dictionary, Postings
from bs4 import BeautifulSoup
from bs4 import Comment
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

start_time = time.time()
stops = set(stopwords.words("english"))

def main():
	
	urls = []
	index = {}
	total_docs = 0
	for counter in range(75):
		path = 'WEBPAGES_RAW/' + str(counter)
		for filename in os.listdir(path):
			file_path = path + "/" + filename	
			try:
				file = open(file_path)
				soup = BeautifulSoup(file, 'html.parser')
				soup = clean_html(soup);
				#docID is made of folder number concatenated with _filename
				docId = str(counter) + "_" + filename
				total_docs += 1
				title = extract_title(soup)

				# commented print for now so that it doesn't slow down the processing
				# if title:
				# 	print "Title : " + title
				
				content = extract_content(soup)
				if content:
					# commented print for now so that it doesn't slow down the processing
					# print "Content\n"
					text = '\n'.join([x for x in content.split("\n") if x.strip()!=''])			
					tokens = generate_tokens(text)

					# might look complicated at first
					# iterate over all the words that we obtained
					for k, v in tokens.iteritems():
						# create new object for Dictionary (referring index terminology) with only 'term' for now 
						# TODO: Figure out the docFrequency part
						obj_dict = Dictionary(k)

						# create the postings object with docID and term frequency
						obj_postings = Postings(docId, v) 
						if obj_dict in index:
							index[obj_dict].insert(len(index[obj_dict]),obj_postings)
						else:
							index[obj_dict] = list()
							index[obj_dict].insert(0,obj_postings)
				# however, printing doc number so that we know about the progress
				print "Document %s processed" % (str(total_docs))

			except Exception as e:
				print e
				print "Exception occured"
				pass

	print tokens
	with open('index.txt','w') as index_file:
		for k, v in index.iteritems():
			doc_frequency = len(v)
			index_file.write(str(k.term) + " -> ")
			postings_list = ""
			for posting in v:
				tf_idf = calculate_tfIdf(posting.term_frequency, doc_frequency, total_docs)
				postings_list += '[%s,%s,%s],' % (posting.docID, posting.term_frequency, str(tf_idf))
			postings_list = postings_list[:-1]
			index_file.write(postings_list +'\n')
		index_file.write(" Tokens generated : " + str(len(index)))
	

	print " Tokens generated : " + str(len(index))
	print ("--- %s seconds ---" % (time.time() - start_time))
	print("documents processed -> " + str(total_docs))
	
def calculate_tfIdf(tf, df, N):
	# although the base of the log doesn't matter in this calculation
	# but just for the sake of it, calculating with base 10
	idf = math.log(N/df, 10)
	tf_idf = (1 + math.log(tf,10)) * idf
	return format(tf_idf, '.2f')

def clean_html(soup):
	''' Input : DOM object of the html page
		Output: DOM object of the html page with script tags, style tags and comments removed

		The method removes all <script>, and <style> tags. 
		It also removes all the comments from the html code 
	'''

	# Remove script tags
	script_tags = soup.findAll('script')
	for item in script_tags:
	    item.extract()

	#remove style tags
	style_tags = soup.findAll('style')
	for item in style_tags:
	    item.extract()

	#remove comments
	comments = soup.findAll(text=lambda text:isinstance(text, Comment))
	[comment.extract() for comment in comments]

	return soup

def extract_title(soup):
	''' Input : DOM object of the html page
		Output: Title extracted from the html page
	'''
	try:
		return soup.title.string
	except Exception:
		print "No title"



def extract_content(soup):
	''' Input : DOM object of the html page
		Output: Text extracted from all HTML tags, except the <head> tag
	'''
	try:
		head_tag = soup.find('head')
		head_tag.extract()
		return soup.getText()
	except Exception:
		print "No body"

def generate_tokens(text):
	'''
		Genrates list of tokens for the text in <body> tag
	'''

	#contains the stopwords imported from nltk.stopwords
	global stops
	porter_stemmer = PorterStemmer()
	tokens = {}
	for line in text.split('\n'):
		line = line.strip().lower()
		line = re.sub('[^0-9a-zA-Z\' ]+', ' ', line)
		for word in line.split(' '):
			#if word, and word not a stopword
			if len(word) > 0 and word not in stops:
				word = porter_stemmer.stem(word)
				
				#tokens is now a dictionary string -> int: (term, count) pair
				if str(word) in tokens:
					tokens[str(word)] += 1
				else:
					tokens[str(word)] = 1
	return tokens

if __name__ == '__main__':
  main()
