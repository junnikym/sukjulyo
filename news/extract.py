# -*- coding: utf-8 -*-

import subprocess
import json

from rss_parser import RssParser
#from ner import NER

SERVER_URL = 'http://localhost:8080'

rss_parser = RssParser()
#ner = NER()

result = rss_parser.extraction()
print(len(result))
for article in result:
	text = f"{article['title']}\n{article['description']}"
	
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
