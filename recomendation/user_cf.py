'''
	[ factor ]

	1. Client ID
	2. Hashtag
	3. Score

'''

import numpy as np
from numpy.lib.function_base import delete
import pandas as pd

from surprise import SVD, Dataset, accuracy, Reader
from surprise.model_selection import train_test_split, GridSearchCV

'''
	test client datas
	[ Client ID, Hashtag, Score ]
'''
TEST_DATA_DF_HEADER = ['client_id','hashtag','score']
TEST_DATA_DF = pd.DataFrame(
	np.array([
		[1, 0, 100], 
		[1, 1, 20],
		[1, 2, 40],
		[1, 3, 80],
		[1, 4, 40],
		[1, 5, 100],
		[1, 6, 85],

		[2, 4, 30],
		[2, 5, 120],
		[2, 6, 95],
		[2, 7, 110],
	]),
	columns = TEST_DATA_DF_HEADER
)

TEST_DATA_HASH = {
	0: '영화', 
	1: '봉준호', 
	2: '헐리우드', 
	3: '타란티노', 
	4: '손흥민', 
	5: '프리미어리그', 
	6: '메시',
	7: '호날두'
}

data_df = TEST_DATA_DF
algorithm = SVD
client_id = 2
clinet_id_key = 'client_id'
hashtag_key = 'hashtag'
score_key = 'score'

reader = Reader( rating_scale=(
	data_df[score_key].min(),
	data_df[score_key].max() 
))
data = Dataset.load_from_df(data_df, reader)
#trainset, testset = train_test_split(data, test_size=0.25, random_state=0)
trainset = data.build_full_trainset()

algo = SVD(n_factors=50, random_state=0)
algo.fit(trainset=trainset)

potential_tags_list = data_df.loc\
						[data_df[clinet_id_key]==client_id]\
						[hashtag_key]\
						.to_list()

potential_tags = [
	item \
	for item in TEST_DATA_HASH.keys() \
		if not item in potential_tags_list
]

for item in potential_tags:
	pred = algo.predict(uid=client_id, iid=item)
	print(TEST_DATA_HASH[item], ' -> ', pred.est)