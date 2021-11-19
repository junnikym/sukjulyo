# -*- coding: utf-8 -*-

import sys

import pandas as pd
import numpy as np

import json 
import feedparser
from html.parser import HTMLParser

import datetime
from dateutil.parser import parse as DateParse


class RssParser:

	def __init__(
		self,
		rss_urls_json_file = './rss.json',
		search_list=['title', 'link', 'description', 'author'],
		default_values={'title': '', 'link': '', 'description': '',
                  'author': None, 'category': []},
		print_err = True
	) -> None:
		self.rss_urls_json_file	= rss_urls_json_file
		self.search_list		= search_list
		self.default_values		= default_values
		self.print_err 			= print_err

		self.error_list = set()



	def text_parser(self, text):
		'''
		Convert HTML Entity to Normal Latter
		'''
		html_parser = HTMLParser()
		text = html_parser.unescape(text)
		return text



	def fine_elems_on_article(self, item, rss_info):
		result = {}

		if item.has_key('pubdate'):
			result['pubDate'] = DateParse(item['pubdate']).date().strftime('%Y-%m-%d %H:%M:%S')
		elif item.has_key('pubDate'):
			result['pubDate'] = DateParse(item['pubDate']).date().strftime('%Y-%m-%d %H:%M:%S')
		else:
			self.error_list.add('pubDate')
			result['pubDate'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		for target in self.search_list:

			if item.has_key(target):
				result[target] = self.text_parser(item[target])
			else:
				self.error_list.add(target)
				result[target] = self.default_values[target]

		return result;



	def extraction(self):
		news = []

		with open(self.rss_urls_json_file) as json_file:
			rss_infos = json.load(json_file)
			
			for rss_info in rss_infos:

				try:
					articles = feedparser.parse(rss_info['url']).entries
				except:
					print(f"Can not open RSS URL : {rss_info}")
				
				if articles:
					for item in articles:
						news.append(self.fine_elems_on_article(item, rss_info))
						news[-1]['corp'] = rss_info['corp']
						news[-1]['cate'] = rss_info['cate']
				else:
					if self.print_err:
						print(f"{rss_info['corp']} - {rss_info['cate']} is closed or empty")

			print("Some RSS can not find those : ", self.error_list)

		return news;
