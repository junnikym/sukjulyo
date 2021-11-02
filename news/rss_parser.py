# -*- coding: utf-8 -*-

import sys
import datetime

import pandas as pd
import numpy as np

import argparse
import json 
from xml.etree import ElementTree   # xml 파싱 모듈 import

if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib import urlopen

class RssParser:

	def __init__(
		self,
		rss_urls_json_file = './rss.json',
		search_list_single = ['title', 'link', 'description', 'author', 'pubDate'],
		search_list_multi = ['category',],
		default_values = {'title':'', 'link':'','description':'','author':None,'pubDate':datetime.datetime.now(),'category':[]},
		print_err = True
	) -> None:
		self.rss_urls_json_file	= rss_urls_json_file
		self.search_list_single = search_list_single
		self.search_list_multi	= search_list_single
		self.default_values		= default_values
		self.print_err 			= print_err

	def open_rss_url(self, url, rss_info):
		try:
			response = urlopen(url).read()
		except:
			if self.print_err:
				print(" *Error : Can not open url ( ", rss_info['corp'], ")")	
			return
		
		try:
			response = response.decode('UTF8')
		except:
			response = response.decode('CP949')

		xml_tree = ElementTree.fromstring(response)
		
		return list(xml_tree.iter('item'))


	def fine_elems_on_article(self, item):
		result = {}

		for target in self.search_list_single:
			elem = item.find(target)

			if (elem != None) and (elem.text != None) :
				result[target] = elem.text;
			else:
				if(target == 'pubDate'):
					result[target] = self.default_values[target].strftime('%Y-%m-%d')
				else:
					result[target] = self.default_values[target]

		for target in self.search_list_multi:
			elem = item.findall(target)

			if (elem != None) and (len(elem) != 0) :
				result[target] = [x.text for x in elem];
			else:
				result[target] = self.default_values[target]

		return result;

	def extraction(self):
		news = []

		with open(self.rss_urls_json_file) as json_file:
			rss_infos = json.load(json_file)
			
			for rss_info in rss_infos:		
				articles = self.open_rss_url(rss_info['url'], rss_info)
				if articles:
					for item in articles:
						news.append(self.fine_elems_on_article(item))
						news[-1]['corp'] = rss_info['corp']
						news[-1]['cate'] = rss_info['cate']
				else:
					if self.print_err:
						print(f"{rss_info['corp']} - {rss_info['cate']} is closed or empty")

		return news;
