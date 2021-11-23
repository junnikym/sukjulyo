import numpy as np
from numpy.lib.function_base import average
import pandas as pd

from sklearn.neighbors import KernelDensity

import seaborn as sns
import matplotlib.pyplot as plt

import requests
import json
import datetime

SERVER_URL = 'http://localhost:8080'
TIME_FORM = '%Y-%m-%dT%H:%M:%S'

class Topic:

	def __init__(
		self, 
		percentile=0.25,
		n_issue_tags=3,
		n_offset = 0
	) -> None:
		self.percentile = percentile
		self.n_issue_tags = n_issue_tags
		self.n_offset = n_offset


	def _parse_to_hour(self, x: str):
		x = x.lower()
		if x == 'day':
			return 24
		elif x == 'week':
			return 24*7
		else:
			print(" error at recommendation / topic - wrong input (period) ")

		return None


	def get_freq(self, period: str, duration: str, parse_to_hour=True):

		period = period.upper()
		if parse_to_hour:
			duration = self._parse_to_hour(duration)

		today_t = datetime.datetime.now().strftime("%Y-%m-%dT00:00:00")
		start_t = (
			datetime.datetime.strptime(today_t, TIME_FORM)
			- datetime.timedelta(hours=duration)
		).strftime(TIME_FORM)
		end_t = (
			datetime.datetime.strptime(today_t, TIME_FORM)
			+ datetime.timedelta(hours=23, minutes=59, seconds=59)
		).strftime(TIME_FORM)

		today = datetime.datetime.now().strftime("%d")

		headers = {'Content-Type': 'application/json; charset=utf-8'} 
		cookies = {'access': 'sorryidontcare'}

		top_tag_res = requests.get(
			f"{SERVER_URL}/hashtag/freq?period={period}&limit={self.n_issue_tags}&offset={self.n_offset}&start={start_t}&end={end_t}",
			headers=headers
		)

		if top_tag_res.status_code == 200:
			data = json.loads(json.dumps(top_tag_res.json()))

			all_avr = 0
			all_num = 0
			avr_freq = []
			dates = set([int(x['date']) for x in data])
			for d in dates:
				num = 0
				avr_freq.append({'date': d, 'freq': 0})
				tags = list(filter(lambda x: int(x['date']) == d, data))

				for t in tags:
					avr_freq[-1]['freq'] += t['freq']
					num += 1

					all_avr += t['freq']
					all_num += 1

				avr_freq[-1]['freq'] /= num

			return data, sorted(avr_freq, key=lambda x: x['freq'], reverse=True), today, (all_avr/all_num)

		return None;

	
	def get_issues(self, period, duration, parse_to_hour=False):

		tags, avr_freq, today, all_avr = self.get_freq(period, duration, parse_to_hour=parse_to_hour)
		if not tags or not avr_freq or not today or not all_avr:
			return

		today_i = None
		for i in range(len(avr_freq)):
			if int(avr_freq[i]['date']) == int(today):
				today_i = i+1
				break;

		if today_i == None:
			return None

		if (today_i/len(avr_freq)) <= self.percentile:
			return list(filter(lambda x: int(x['date']) == int(today) and int(x['freq']) >= all_avr, tags))

		else:
			return None;


#topic = Topic()
#topic.get_issues('DAY', 24, parse_to_hour=False)
