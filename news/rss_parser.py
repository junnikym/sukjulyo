# -*- coding: utf-8 -*-

import sys
import datetime

import pandas as pd
import numpy as np

import json 
from xml.etree import ElementTree   # xml 파싱 모듈 import

if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib import urlopen

RSS_JSON_PATH = '../../news/rss.json'

def open_rss_url(url):
	try:
		response = urlopen(url).read()
	except:
		print(" *Error : Can not open url ( ", rss_info['corp'], ")")	
		return
	
	try:
		response = response.decode('UTF8')
	except:
		response = response.decode('CP949')

	xml_tree = ElementTree.fromstring(response)
	
	return list(xml_tree.iter('item'))

#articles = open_rss_url(url)
#print(articles[2].find('title').text)

news = []

LIST_SEARCH_SINGLE = [
	'title', 'link', 'description', 'author', 'pubDate', 
]

LIST_SEARCH_MULTI = [
	'category',
]

DEFAULT_VAL = {
	'title'			 : '',
	'link'			 : '',
	'description'	 : '',
	'author'		 : None,
	'pubDate'		 : datetime.datetime.now(),
	'category'		 : []
}

def fine_elems_on_article(item):
	result = {}

	for target in LIST_SEARCH_SINGLE:
		elem = item.find(target)

		if (elem != None) and (elem.text != None) :
			result[target] = elem;
		else:
			result[target] = DEFAULT_VAL[target]

	for target in LIST_SEARCH_SINGLE:
		elem = item.findall(target)

		if (elem != None) and (len(elem) != 0) :
			result[target] = [x.text for x in elem];
		else:
			result[target] = DEFAULT_VAL[target]

	return result;

with open(RSS_JSON_PATH) as json_file:
	rss_infos = json.load(json_file)
	
	for rss_info in rss_infos:		
		articles = open_rss_url(rss_info['url'])
		if articles:
			for item in articles:
				news.append(fine_elems_on_article(item))
		else:
			print(f"{rss_info.corp} - {rss_info.cate} is closed or empty")

print(news)
