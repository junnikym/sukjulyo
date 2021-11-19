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

#RESTART_NUM = 8902
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

	text = f"{article['title']}\n{article['description']}"
	splited_text = text.split()

	str_i = 0
	str_buf = splited_text[str_i]
	list_of_word_for_article = set()

	while True:	
		p=''
		if str_i < len(splited_text):
			p = splited_text[str_i]
			str_i+=1
		elif str_buf != '':
			break;

		if sys.getsizeof(str_buf) < 512:
			if sys.getsizeof(p) > 512:
				continue

			s = str_buf + ' ' + p
			if sys.getsizeof(s) < 512:
				str_buf = s
				continue

		list_of_ner_word, test = ner.predict(p)
		str_buf = p

		for it in list_of_ner_word[::]:
			if it['tag'] in SKIP_TAGS:
				list_of_ner_word.remove(it)
				continue

			list_of_word_for_article.add(it['word'].strip())

	article['hashtags'] = list(list_of_word_for_article)

	save(article)
	pbar.update(1)
