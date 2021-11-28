from re import search
import requests
import json

import pandas as pd

from topic import Topic 
from latent_factor_collaborative_filter import LatentFactorCollaborativeFilter
from content_based_filter import ContentBasedFilter

SERVER_URL = 'http://localhost:8080'
N_HASHTAG = 5
N_PART_RESULT = 4

class Recommendation():
	
	def __init__(self, data_dir) -> None:
		self.DATA_DIR = data_dir

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
		self.news_df = pd.read_csv(f'{self.DATA_DIR}/news.csv')
		self.news_df['hashtags'] = (self.news_df['hashtags'].fillna("")).apply(
			lambda x: x.split('|')
		)

		self.hashtags_df = pd.read_csv(f'{self.DATA_DIR}/hashtags.csv', index_col=0)\
            .rename(columns={"id": "hashtagId"})[['hashtagId', 'tag']]
		self.scores_df = pd.read_csv(f'{self.DATA_DIR}/scores.csv', index_col=0).drop(['id'], axis=1)

		'''
		ratings_df :
			contents_df 데이터의 User, Item, Rating 3가지 컬럼을 순서대로 배치
		'''
		self.contents_df = pd.merge(self.hashtags_df, self.scores_df, on='hashtagId', how='outer')

		if 'content_based_filter' in self.__dict__.keys():
			self.content_based_filter.set_contents(self.news_df, 'hashtags')

	def predict(self, client_id):
		news_result = []
		hashtag_result = []
		not_first_news = []

		n_rest_of_not_first = 0

		''' --------------------------------------------------
		Get Issue Topic
		-------------------------------------------------- '''
		issue_tags = self.topic.get_issues('DAY', 'WEEK', parse_to_hour=True)
		if issue_tags:
			hashtag_result.extend(issue_tags)
			news = self.content_based_filter.predict(issue_tags, result_size=N_PART_RESULT, print_result=False)
			if news:
				news_result.append(news[0][1])
				if len(news) > 1: not_first_news.extend([x[1] for x in news[1:]])

			n_rest_of_not_first += N_PART_RESULT - len(news)
		else:
			n_rest_of_not_first += N_PART_RESULT

		''' --------------------------------------------------
		Get from latent-CF
		-------------------------------------------------- '''
		lcf = self.latent_cf.predict(client_id, top_n=N_HASHTAG)
		lcf = lcf[(lcf.est >= 15.0)]
		if lcf.count().tag:
			lcf = lcf['tag'].values
			hashtag_result.extend(lcf)
			news = self.content_based_filter.predict(lcf, result_size=N_PART_RESULT, print_result=False)
			if news:
				news_result.append(news[0][1])
				if len(news) > 1: not_first_news.extend([x[1] for x in news[1:]])

			n_rest_of_not_first += N_PART_RESULT - len(news)

		''' --------------------------------------------------
		Get from conten-based-filter
		-------------------------------------------------- '''
		# < Client Data >
		client_genres = requests.get(f'{SERVER_URL}/hashtag/client/{client_id}?size={N_HASHTAG}&sort=score&direction=desc').json()
		client_genres = json.loads(json.dumps(client_genres))
		client_genres = [x['hashtag']['tag'] for x in client_genres]
		
		hashtag_result.extend(client_genres)

		# < Target Data >
		n_rest = 3-len(news_result) + n_rest_of_not_first

		cbf = self.content_based_filter.predict(client_genres, print_result=False, result_size=n_rest)
		if cbf:
			news_result.extend([x[1] for x in cbf[:n_rest]])
			news_result.extend(not_first_news)
			news_result.extend([x[1] for x in cbf[n_rest:]])

		return news_result, hashtag_result
