import numpy as np
from numpy.lib.function_base import average
import pandas as pd

from sklearn.neighbors import KernelDensity

import seaborn as sns
import matplotlib.pyplot as plt

import requests
import datetime

SERVER_URL = 'http://localhost:8080'
TIME_FORM = '%Y-%m-%dT%H:%M:%S'

class Topic:

	def __init__(
		self, 
		n_issue_tags=25, 
		n_all_tags=1000, 
		n_gap=5, 
		allow_gradient=10,
		min_freq=200
	) -> None:
		self.n_issue_tags = n_issue_tags
		self.n_all_tags = n_all_tags
		self.n_gap = n_gap
		self.allow_gradient = allow_gradient
		self.min_freq = min_freq

	def get_most_freq_tags(self, period: str):

		period = period.lower()
		period_to_hour = 0
		if period == 'day':
			period_to_hour = 24
		else:
			print(" error at recommendation / topic - wrong input (period) ")

		start_t = datetime.datetime.now().strftime("%Y-%m-%dT00:00:00")
		end_t = (
			datetime.datetime.strptime(start_t, TIME_FORM) 
			+ datetime.timedelta(hours=period_to_hour)
		).strftime(TIME_FORM)
		today = datetime.datetime.now().strftime("%d")

		headers = {'Content-Type': 'application/json; charset=utf-8'} 
		cookies = {'access': 'sorryidontcare'}

		top_tag_res = requests.get(
			f"{SERVER_URL}/hashtag/freq?period=DAY&limit={self.n_all_tags}&offset={self.n_all_tags-1}&start={start_t}&end={end_t}",
			#f"http://localhost:8080/hashtag/freq?period=DAY&limit={self.n_issue_tags}&offset=8&start=2021-11-06T00:00:00&end=2021-11-16T23:59:59",
			headers=headers
		)

		top_tag = top_tag_res.json()
		tag_avr = {}
		total_avr = 0
		print(top_tag)
		[tag_avr.update({it['date']: 0}) for it in top_tag]

		for tag in top_tag:
			tag_avr[tag['date']] += int( tag['freq'] )
		for k in tag_avr.keys():
			tag_avr[k] /= self.n_issue_tags
			total_avr += tag_avr[k]
		total_avr /= len(tag_avr)

		print(tag_avr)
		print(tag_avr['6'])
		print(total_avr)

		if tag_avr[str(today)] == total_avr:
		#if tag_avr['6'] >= total_avr:
			today_tag_res = requests.get(
				f"{SERVER_URL}/hashtag/freq?limit={self.n_all_tags}&offset=0&start={start_t}&end={end_t}",
				#"http://localhost:8080/hashtag?limit=10&offset=8&start=2021-11-06T00:00:00&end=2021-11-16T23:59:59",
				headers=headers
			)

			return today_tag_res.json()

		return None;
	
	def get_issues(self, period):

		tags = self.get_most_freq_tags(period);
		if tags == None:
			return
		
		result = []
		for i in range(0, self.n_issue_tags):
			a = -(tags[i+self.n_gap]['freq'] - tags[i]['freq']) / self.n_gap
			if a > self.allow_gradient and tags[i]['freq'] > self.min_freq:
				result.append(tags[i])

		print(result)

		#pd.json_normalize(tags).plot.kde()
		#plt.show()

		# if hashtag_frequency is over than limit => return hashtag
		return result


topic = Topic()
topic.get_issues('DAY');


#plt.plot(test_df['tag'], test_df['freq'])
#plt.show()

#kde = KernelDensity(bandwidth=1.0, kernel='gaussian')
#kde.fit(test_df[:, None])

#print(kde)

#sns.distplot(test_df['tag'], bins=10, kde=True, rug=True)
#plt.show()
