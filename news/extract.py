# -*- coding: utf-8 -*-
import sys
import os

from pickle import NONE
import requests

from tqdm import tqdm

from rss_parser import RssParser
from ner import NER

import kss
import json

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

RESTART_NUM = 1
#RESTART_NUM = None

PROJECT_DIR = os.getcwd()
DATA_DIR = f'{PROJECT_DIR}/../summary/ext/ext/data'
RAW_DATA_DIR = f'{DATA_DIR}/raw'

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
		

def korean_sent_spliter(doc):
    sents_splited = kss.split_sentences(doc)
    if len(sents_splited) == 1:
        # .이나 ?가 있는데도 kss가 분리하지 않은 문장들을 혹시나해서 살펴보니
        # 대부분 쉼표나 가운데점 대신 .을 사용하거나 "" 사이 인용문구 안에 들어가있는 점들. -> 괜찮.
        # aa = sents_splited[0].split('. ')
        # if len(aa) > 1:
        #     print(sents_splited)
        return sents_splited
    else:  # kss로 분리가 된 경우(3문장 이상일 때도 고려)
        #print(sents_splited)
        for i in range(len(sents_splited) - 1):
            idx = 0
            # 두 문장 사이에 .이나 ?가 없는 경우: 그냥 붙여주기
            if sents_splited[idx][-1] not in ['.', '?'] and idx < len(sents_splited) - 1:
                sents_splited[idx] = sents_splited[idx] + ' ' + sents_splited[idx + 1] if doc[len(sents_splited[0])] == ' ' \
                    else sents_splited[idx] + sents_splited[idx + 1]
                del sents_splited[idx + 1]
                idx -= 1
        #print(sents_splited)
        return sents_splited


rss_result = rss_parser.extraction()
print(f' {len(rss_result)} numbers article finded')

if RESTART_NUM == None:
	with open(f"{RAW_DATA_DIR}/data.jsonl", encoding="utf-8", mode="w+") as f:
		f.write('')

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
	if _title == '' or _description == '':
		pbar.update(1)
		continue

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

	news_sent = None
	jsonl_elem = None
	try:
		news_sent = korean_sent_spliter(text)
		jsonl_elem = {'article_original': news_sent, "link": article['link']}
	except:
		print(news_sent)
		jsonl_elem = {'article_original': [text], "link": article['link']}

	with open(f"{RAW_DATA_DIR}/data.jsonl", encoding="utf-8", mode="a+") as f:
		dupmed_it = json.dumps(jsonl_elem, ensure_ascii=False)
		f.write(dupmed_it + "\n")

	pbar.update(1)

cur_dir = os.getcwd()
os.chdir(f'{cur_dir}/../recommendation/')
os.system('python update_data.py')

cur_dir = os.getcwd()
os.chdir(f'{cur_dir}/../summary/')
os.system('python summarization.py')
