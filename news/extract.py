# -*- coding: utf-8 -*-

import requests
import json

from rss_parser import RssParser
from ner import NER

SERVER_URL = 'http://localhost:8080/news'

'''
	개체이름:
        사람이름(PER), 지명(LOC),
        기관명(ORG), 기타(POH)

	시간표현:
		날짜(DAT), 시간(TIM), 기간(DUR)

	수량표현:
		통화(MNY), 비율(PNT), 기타 수량표현(NOH)
'''
SKIP_TAGS = ['DAT', 'TIM', 'DUR', 'MNY', 'PNT', 'NOH']

rss_parser = RssParser()
ner = NER()

count = 0

def save(article):
	global count 
	count += 1

	article['pubDate'] = article.pop('pubdate')

	res = requests.post(SERVER_URL, json=article)

	if res.status_code != 200:  # ERROR
		print(res.json())
		

result = rss_parser.extraction()
#list_of_word_for_all = {}

for article in result:
	text = f"{article['title']}\n{article['description']}"

	list_of_ner_word, test = ner.predict(text)
	list_of_word_for_article = set()

	for it in list_of_ner_word[::]:
		#print(item)
		if it['tag'] in SKIP_TAGS:
			list_of_ner_word.remove(it)
			continue

		list_of_word_for_article.add(it['word'].strip())

	article['hashtags'] = list(list_of_word_for_article)

	#for k in list_of_word_for_article.keys():
	#	if list_of_word_for_article[k] in list_of_word_for_all.keys():
	#		list_of_word_for_all[k] += list_of_word_for_article[k]
	#	else:
	#		list_of_word_for_all[k] = list_of_word_for_article[k]

	save(article)
