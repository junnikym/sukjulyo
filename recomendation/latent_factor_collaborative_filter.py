import os

# For MacOS
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

from surprise import SVD, Dataset, accuracy, Reader
from surprise.model_selection import train_test_split, GridSearchCV

import numpy as np
import pandas as pd

RATING_MIN = 0.5
RATING_MAX = 15.0

class LatentFactorCollaborativeFilter:

	def __init__( 
		self, 
		ratings_df: pd.DataFrame, 
		contents_df: pd.DataFrame,
		rating_range=(RATING_MIN, RATING_MAX),
		is_include_timestamp=False, 
		is_run_test=False,
		uid = 'uid',
		iid = 'iid'
	) -> None:

		if not ratings_df.empty:
			self.set_contents_df(contents_df)

		if not ratings_df.empty:
			self.set_ratings_df(
				ratings_df, 
				rating_range=rating_range,
				is_include_timestamp=is_include_timestamp, 
				is_run_test=is_run_test
			)

		self.set_id_col(uid, iid)

	def set_id_col(self, uid, iid):
		self.uid = uid;
		self.iid = iid;

	def set_contents_df(self, contents_df):
		self.contents_df = contents_df

	def set_ratings_df(
		self, 
		ratings_df, 
		rating_range=(RATING_MIN, RATING_MAX), 
		is_include_timestamp=False, 
		is_run_test=False
	) -> None:
		self.ratings_df = ratings_df
		
		reader = Reader(
            line_format='user item rating' + (' timestamp' if is_include_timestamp else ''),
            sep=',',
            rating_scale=rating_range
        )
		data = Dataset.load_from_df(ratings_df, reader)

		self.algo = SVD(n_epochs=20, n_factors=50, random_state=0)
		
		if is_run_test:
			trainset, self.testset = train_test_split(data, test_size=0.25, random_state=0)
			self.algo.fit(trainset)
			
			predictions = self.algo.test(self.testset)
			accuracy.rmse(predictions)

		else:
			trainset = data.build_full_trainset()
			self.algo.fit(trainset)

	def get_unread_contents(self, target_user_id):
		read = self.ratings_df \
					[self.ratings_df[self.uid] == target_user_id] \
					[self.iid] \
					.tolist()

		total = self.contents_df[self.iid].tolist()
		unread = [it for it in total if it not in read]

		print(read)

		return unread

	def predict(self, target_user_id, unread=None, top_n=100):

		if not unread:
			unread = self.get_unread_contents(target_user_id)

		#predictions = [algo.predict(str(user_id), str(item)) for item in unread]
		predictions = [self.algo.predict(target_user_id, item) for item in unread]

		predictions.sort(key=lambda pred: pred.est, reverse=True)
		top_predictions = pd.DataFrame(predictions[:top_n])
		top_predictions.rename(columns={'iid': self.iid}, inplace=True)

		top_contens = self.contents_df[
			self.contents_df[self.iid].isin(
				top_predictions[self.iid]
			)
		]

		return pd.merge(top_predictions, top_contens, on=self.iid)


hashtags_df = pd.read_csv('data/hashtags.csv', index_col=0)\
    			.rename(columns={"id": "hashtagId"})[['hashtagId', 'tag']]
scores_df = pd.read_csv(
	'data/scores.csv', index_col=0).drop(['id'], axis=1)
print(scores_df)
contents_df = pd.merge(hashtags_df, scores_df, on='hashtagId', how='outer')

'''
ratings_df :
	contents_df 데이터의 User, Item, Rating 3가지 컬럼을 순서대로 배치
'''

latent_cf = LatentFactorCollaborativeFilter(
	scores_df,
	hashtags_df,
	uid='clientId',
	iid='hashtagId'
)
print(latent_cf)

print(latent_cf.predict(123))
