# -*- coding: utf-8 -*-
import sys

from pickle import NONE
import requests

from tqdm import tqdm

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

#RESTART_NUM = 2000
RESTART_NUM = None

rss_parser = RssParser()
ner = NER()


def checkExistence(link):
	res = requests.get(f'{SERVER_URL}/exists?link={link}')
	return res.json()

def save(article):
	global count 

	res = requests.post(SERVER_URL, json=article)

	if res.status_code != 200:  # ERROR
		print(res.json())
		

rss_result = rss_parser.extraction()
print(f' {len(rss_result)} numbers article finded')

pbar = tqdm(total=len(rss_result))
start_i = 0
if RESTART_NUM:
	start_i = RESTART_NUM
	pbar.update(RESTART_NUM)

for i in range(start_i, len(rss_result)):
	article = rss_result[i]

	if checkExistence(article['link'].replace('&', '%26')):
		pbar.update(1)
		continue

	_title = article['title'] if 'title' in article.keys() else ''
	_description = article['description'] if 'description' in article.keys() else ''
	text = f'{_title}\n{_description}'
	splited_text = list(reversed(text.split()))
	if not splited_text:
		pbar.update(1)
		continue

	str_i = 0
	str_buf = ''
	list_of_word_for_article = set()
	p = ''

	while True:
		if not splited_text:
			break
		
		if sys.getsizeof(str_buf) < 512:
			p = splited_text.pop()

			if sys.getsizeof(p) > 512:
				p = ''
				continue

			s = str_buf + ' ' + p
			if sys.getsizeof(s) < 512:
				str_buf = s
				continue
			
			else:
				splited_text.append(p)

		list_of_ner_word, test = ner.predict(str_buf)
		str_buf = ''

		for it in list_of_ner_word[::]:
			if it['tag'] in SKIP_TAGS:
				list_of_ner_word.remove(it)
				continue

			list_of_word_for_article.add(it['word'].strip())

	article['hashtags'] = list(list_of_word_for_article)

	save(article)
	pbar.update(1)
