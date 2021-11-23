from re import search
import requests
import json

import pandas as pd

from topic import Topic 
from latent_factor_collaborative_filter import LatentFactorCollaborativeFilter
from content_based_filter import ContentBasedFilter

SERVER_URL = 'http://localhost:8080'
N_HASHTAG = 5


class Recommendation():
	
	def __init__(self) -> None:
		self.update()

		self.topic = Topic()

		self.latent_cf = LatentFactorCollaborativeFilter(
			self.scores_df,
			self.hashtags_df,
			uid='clientId',
			iid='hashtagId'
		)

		self.content_based_filter = ContentBasedFilter()
		self.content_based_filter.set_contents(self.news_df, 'hashtags')

	def update(self) -> None:
		self.news_df = pd.read_csv('data/news.csv')
		self.news_df['hashtags'] = (self.news_df['hashtags'].fillna("")).apply(
			lambda x: x.split('|')
		)

		self.hashtags_df = pd.read_csv('data/hashtags.csv', index_col=0)\
            .rename(columns={"id": "hashtagId"})[['hashtagId', 'tag']]
		self.scores_df = pd.read_csv('data/scores.csv', index_col=0).drop(['id'], axis=1)

		'''
		ratings_df :
			contents_df 데이터의 User, Item, Rating 3가지 컬럼을 순서대로 배치
		'''
		self.contents_df = pd.merge(self.hashtags_df, self.scores_df, on='hashtagId', how='outer')

		if 'content_based_filter' in self.__dict__.keys():
			self.content_based_filter.set_contents(self.news_df, 'hashtags')

	def predict(self, client_id):
		result = []

		''' --------------------------------------------------
		Get Issue Topic
		-------------------------------------------------- '''
		issue_tags = self.topic.get_issues('DAY', 24, parse_to_hour=False)
		if issue_tags:
			news = self.content_based_filter.predict(issue_tags, result_size=1, print_result=False)
			if news:
				result.append(news[0][1])

		''' --------------------------------------------------
		Get from latent-CF
		-------------------------------------------------- '''
		lcf = self.latent_cf.predict(client_id, top_n=N_HASHTAG)
		lcf = lcf[(lcf.est >= 15.0)]
		if lcf.count().tag:
			lcf = lcf['tag'].values
			news = self.content_based_filter.predict(
				lcf, result_size=1, print_result=False)
			if news:
				result.append(news[0][1])

		''' --------------------------------------------------
		Get from conten-based-filter
		-------------------------------------------------- '''
		# < Client Data >
		client_genres = requests.get(
			f'{SERVER_URL}/hashtag/client/{client_id}?size={N_HASHTAG}&sort=score&direction=desc').json()
		client_genres = json.loads(json.dumps(client_genres))
		client_genres = [x['hashtag']['tag'] for x in client_genres]

		# < Target Data >
		cbf = self.content_based_filter.predict(client_genres, print_result=False)
		if cbf:
			n_rest = 3-len(result)
			for i in range(n_rest):
				result.append(cbf[i][1])

		return result
