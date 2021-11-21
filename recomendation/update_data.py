from sys import path
import requests
import pandas as pd
import json

SERVER_URL = 'http://localhost:8080'
SAVE_PATH = './data'

N_HASH_LOAD = 1000

def load_scores(id, n_hashtag, n_client):
	res = requests.get(
		f'{SERVER_URL}/hashtag/client?id={id}&n_hashtag={n_hashtag}&n_client={n_client}')
	if res.status_code == 200:
		return json.loads(json.dumps(res.json()))


def load_hashtags():
	page = 0
	result = []
	while True:
		res = requests.get(f'{SERVER_URL}/hashtag?page={page}&size={N_HASH_LOAD}')
		
		if res.status_code == 200:
			temp = json.loads(json.dumps(res.json()))
			if not temp:
				break

			result.extend(temp)
		else:
			print("[ ERROR ] Can't load hashtag data")
			break

		page += 1

	return result


def load_news(size):
	res = requests.get(f'{SERVER_URL}/news?period=DAY&size={size}')
	if res.status_code == 200:
		return json.loads( json.dumps( res.json() ) )

def preprocess_news(data):
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


news = load_news(5000)
news_df = preprocess_news(news)
news_df.to_csv(f'{SAVE_PATH}/news.csv', mode='w')


hashtags = load_hashtags()
hashtags_df = pd.DataFrame(hashtags)
hashtags_df.to_csv(f'{SAVE_PATH}/hashtags.csv', mode='w')


scores = load_scores(1982137778, 3, 3)
scores_df = pd.DataFrame(scores)
scores_df.to_csv(f'{SAVE_PATH}/scores.csv', mode='w')
