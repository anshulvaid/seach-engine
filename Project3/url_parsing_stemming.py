# -*- coding: utf-8 -*- 

from __future__ import division
import urllib2
import os
import re
import json
import math
import time
from Index import Dictionary, Postings, Documents
from bs4 import BeautifulSoup
from bs4 import Comment
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from urlparse import urlparse
import sys
import requests
import json, ast
import pprint

reload(sys)
sys.setdefaultencoding('utf-8')
start_time = time.time()
stops = set(stopwords.words("english"))

def main():
	
	urls = []
	index = {}
	total_docs = 0
	documents = {}

	with open('WEBPAGES_RAW/bookkeeping.json') as data_file:    
	  url_data = json.load(data_file)

	for counter in range(75):
		path = 'WEBPAGES_RAW/' + str(counter)
		for filename in os.listdir(path):
			file_path = path + "/" + filename	
			try:
				#docID is made of folder number concatenated with _filename
				docId = str(counter) + "/" + filename
				url = "http://" + url_data[docId]
				# r = requests.get(url)
				# if "text/html" in r.headers["content-type"]:
					# print "Processing url : " + str(url)
				if is_valid_url(docId, url):
					file = open(file_path)
					soup = BeautifulSoup(file, 'html.parser')
					soup = clean_html(soup);
					
					total_docs += 1
					title = extract_title(soup)
					
					content = extract_content(soup)
					if content:
						text = '\n'.join([x for x in content.split("\n") if x.strip()!=''])
						docText = ' '.join([x for x in content.split("\n") if x.strip()!=''])

						document = Documents(docText, title, url)
						documents[docId] = document
						# generate tokens for title and body text
						if title:
							title = ' '.join([x for x in title.split("\n") if x.strip()!=''])
							text =  title + "\n" + text		
						tokens = generate_tokens(text)
						for k, v in tokens.iteritems():
							# create new object for Dictionary (referring index terminology) with only 'term' for now 
							# TODO: Figure out the docFrequency part
							obj_dict = Dictionary(k)
							# create the postings object with docID and term frequency
							obj_postings = Postings(docId, v["count"], v["position"]) 
							if obj_dict in index:
								index[obj_dict].insert(len(index[obj_dict]),obj_postings)
							else:
								index[obj_dict] = list()
								index[obj_dict].insert(0,obj_postings)
					# however, printing doc number so that we know about the progress
					print "Document %s processed" % (str(total_docs))
				# else:
				# 	print "Processing skipped : " + str(url)
			except Exception as e:
				print e
				print "Exception occured"
				pass

	# each json object is modeled af follows:
 	# { "token": "orthogon", 
 	#   "doc_frequency": 3, 
 	#   "postings": [ { "tf-idf": 2.72, "term_frequency": 2, "docID": "0/191",  "position": [ 18,28]} ,..] }

 	#Create a list of json objects
 	json_documents = []
	json_object_list = []
	for k, v in documents.iteritems():
		json_object = {}
		json_object["docId"] = k
		json_object["text"] = v.docText
		json_object["title"] = v.docTitle
		json_object["url"] = v.docLink
		json_documents.append(json_object)

	for k, v in index.iteritems():
		#Each json object is modeled as mentioned in comments above (Refer line : 80 onwards)
		json_object = {}
		json_object["token"] = k.term
		json_object["doc_frequency"] = len(v)
		json_object["postings"] = []
		#create a posting object 
		for posting in v:
			posting_dict = {}
			tf_idf = calculate_tfIdf(posting.term_frequency, len(v), total_docs)
			posting_dict["docID"] = posting.docID
			posting_dict["term_frequency"] = posting.term_frequency
			posting_dict["tf-idf"] = float(tf_idf)
			posting_dict["position"] = posting.position
			json_object["postings"].append(posting_dict)
		json_object_list.append(json_object)

	json_formatted_index = json.dumps(json_object_list, indent = 4)
	json_formatted_index2 = json.dumps(json_documents, indent = 4)
	with open('index.json','w') as index_file:
		index_file.write(json_formatted_index)
	with open('documents.json', 'w') as doc_file:
		doc_file.write(json_formatted_index2)
	print " Tokens generated : " + str(len(index))
	print ("--- %s seconds ---" % (time.time() - start_time))
	print("Documents processed -> " + str(total_docs))										

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

def is_valid_url(docId, url) :

	# for now handling only these many traps, need to find more traps in the bookeeping.json
	traps = ['calendar', 'ganglia', 'butterworth', 'arcus-3', '~mlearn', 'hall_of_fame', 'facebook', 'duttgroup', 'bren/index.php/bren_advance.php']

	# for now, avoiding only these exceptions. These are the most frequent extensions found in bookeeping.json
	file_extensions = {".plg", ".aw", ".hpp ", ".pde", ".project", ".in", ".jpg", ".py", ".rkt", \
											".R", ".r", ".lif", ".java", ".cpp", ".cp", ".py", ".mexglx", ".h", ".opt", \
											".jpg", ".mzn", ".pov", ".db", ".out", ".map", ".txt", ".als", ".xml", ".fig", \
											 ".tst", ".Rnw", ".docx", ".bib", ".pov", ".bat", ".cbproj", ".uu", ".jemdoc", \
											 ".dirs", ".zip/", ".pyc", ".rc2", ".out", ".dsw", ".dsp", ".macros", ".rc",\
											  ".cgi", ".theory", ".rle", ".plg", ".path", ".splay", ".22", ".pdf", ".pde",\
											   ".rkt", ".ff", ".el", ".cc", ".ppt", ".pq", ".frk", ".jpg_ns", ".fasl", ".pl",\
											    ".files", ".hs", ".md", ".xgmml", ".vhd", ".sty", ".LOG", ".am", ".raw", ".intro", \
											    ".rar", ".in", ".sas", ".ypr", ".lif", ".hpp", ".1", ".test", ".grm", ".events", ".css",\
											    ".map", ".mat", ".bst", ".balbst", ".mzn", ".ss", ".m", ".asc"}

	# Checks if the url belongs to the list of traps
	if any(trap in url for trap in traps):
		return False

	#Checks if the url has the extension that belongs to file_extensions	
	parsed = urlparse(url)
	url = parsed[1] + parsed[2]
	# find the occurence of dot character from the end of the url
	index = url.rfind('.')
	extension = url[index:]
	if extension in file_extensions:
		return False
	return True


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
	head_tag = soup.find('head')
	if head_tag:
		head_tag.extract()
	return soup.getText()	

def generate_tokens(text):
	'''
		Genrates list of tokens for the text in <body> tag
	'''

	#contains the stopwords imported from nltk.stopwords
	global stops
	#snowball stemmer imported from nltk.stem
	snowball_stemmer = SnowballStemmer('english')
	tokens = {}
	#tokens is a dictionary with key = string (word) and value = dictionary(count and position list)
	#tokens value is dictionary as follows : {"count" : int, "position" : [list of int]}
	contains_word = False
	#to keep track of the position of the token
	token_position = 0;
	for line in text.split('\n'):
		line = line.strip().lower()
		line = re.sub('[^0-9a-zA-Z\' ]+', ' ', line)
		for word in line.split(' '):
			#if word, and word not a stopword
			if len(word) > 0 and word not in stops:
				# To check if the document contains at least one word. 
				# We ignore documents that contain only numbers
				if word.isalpha():
					contains_word = True
				word = snowball_stemmer.stem(str(word))
				token_position +=1
				if str(word) in tokens:
					tokens[str(word)]["count"] += 1
					tokens[str(word)]["position"].append(token_position)
				else:
					tokens[str(word)] = {}
					tokens[str(word)]["count"] = 1
					tokens[str(word)]["position"] = [token_position]
	
	#If the document contains words, return the token dict
	#If the documnt contains only numbers,return empty dict
	if contains_word:
		return tokens
	else:
		return {}

if __name__ == '__main__':
  main()