# -*- coding: utf-8 -*-

import subprocess
import json

from rss_parser import RssParser
from ner import NER

SERVER_URL = 'http://localhost:8080'

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

def save(article):
	cmd = f'''
		curl --location --request POST '{SERVER_URL}/news' \
		--header 'Content-Type: application/json; charset=UTF-8' \
		--data-raw '{{
			"corp":"{article['corp']}",
			"title":"{article['title']}",
			"link":"{article['link']}",
			"description":"{article['description']}",
			"author":"{article['author']}",
			"pubDate":"{article['pubdate']}"
		}}'
	'''

	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = pipe.communicate()

	state = out.decode().find('state')

	if state != -1:  # ERROR
		print(out)
		

result = rss_parser.extraction()
#list_of_word_for_all = {}

for article in result:
	text = f"{article['title']}\n{article['description']}"

	list_of_ner_word, test = ner.predict(text)
	list_of_word_for_article = {}

	for it in list_of_ner_word[::]:
		#print(item)
		if it['tag'] in SKIP_TAGS:
			list_of_ner_word.remove(it)
			continue

		if it['word'][0] 	== ' ': it['word'] = it['word'][1:]
		if it['word'][-1] 	== ' ': it['word'] = it['word'][0:-1]

		if it['word'] in list_of_word_for_article.keys():
			list_of_word_for_article[it['word']] += 1
		else:
			list_of_word_for_article[it['word']] = 1

	article['hashtags'] = list(list_of_word_for_article.items())

	print(article)

	#for k in list_of_word_for_article.keys():
	#	if list_of_word_for_article[k] in list_of_word_for_all.keys():
	#		list_of_word_for_all[k] += list_of_word_for_article[k]
	#	else:
	#		list_of_word_for_all[k] = list_of_word_for_article[k]

	#save(article)
