from sys import path
import requests
import pandas as pd
import json

SERVER_URL = 'http://localhost:8080/news'
SAVE_PATH = './data/news.csv'

def load(size):
	res = requests.get(f'{SERVER_URL}?period=DAY&size={size}')
	if res.status_code == 200:
		return json.loads( json.dumps( res.json() ) )

def preprocess(data):
	df = pd.DataFrame(None, columns=['id', 'hashtags'])

	for it in data:
		hashtags = ''

		for tag in it['hashtags']:
			if tag['isNoise'] == False:
				hashtags += tag['tag']+'|'

		if hashtags != '' and hashtags[-1] != '|':
			hashtags = hashtags[0:-1]

		df = df.append({'id': it['id'], 'hashtags': hashtags}, ignore_index=True)
		
	return df

news = load(5000)
news_df = preprocess(news)
news_df.to_csv(SAVE_PATH, mode='w')
