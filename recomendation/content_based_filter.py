from numpy import number
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json
import pandas as pd

SERVER_URL = 'http://localhost:8080'
N_HASHTAG = 3

class ContentBasedFilter:

	def __init__(self, contents_df=None, contents_target_col=None) -> None:
		self.count_vectorizer = CountVectorizer()
		if contents_df and contents_target_col:
			self.set_contents(contents_df, contents_target_col)

	def set_contents(self, contents_df, target_col):
		# @TODO: Modify
		self.contents_df = contents_df
		self.target_col = target_col

		self.contents_df[f'{target_col}_literal'] = \
			self.contents_df[target_col].apply(lambda x: (' ').join(x))

	def predict(self, client_tag: list, result_size: int=10, print_result:bool=False) -> list:
		_client_tag = [' '.join(client_tag)]

		self.count_vectorizer.fit_transform(_client_tag)
		
		list_matrix = self.count_vectorizer.transform( 
			self.contents_df[f'{self.target_col}_literal']
		)
		client_matrix = self.count_vectorizer.transform(_client_tag)
		
		tag_sim = cosine_similarity( client_matrix, list_matrix )
		tag_sim_sorted_ind = tag_sim.argsort()[:, ::-1]

		contents_np = self.contents_df.to_numpy()
		result = [contents_np[tag_sim_sorted_ind[0][i]] for i in range(result_size)]

		if print_result:
			for i, e in enumerate(result):
				print(i, ' : ', e)

		return result

'''
Client Data
'''
client_id = 1982137778
client_genres = requests.get(f'{SERVER_URL}/hashtag/client/{client_id}?size={N_HASHTAG}&sort=score&direction=desc').json()
client_genres = json.loads(json.dumps(client_genres))
client_genres = [x['hashtag']['tag'] for x in client_genres]

'''
Target Data
'''
news_df = pd.read_csv('data/news.csv')

news_df['hashtags'] = (news_df['hashtags'].fillna("")).apply(
	lambda x: x.split('|')
)

content_based_filter = ContentBasedFilter()
content_based_filter.set_contents(news_df, 'hashtags')
content_based_filter.predict(client_genres, print_result=True)
