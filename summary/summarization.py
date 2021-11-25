import os
import argparse
import requests

from ext_summarization import ExtSummarization
from abs_summarization import AbsSummarization

PROJECT_DIR = os.getcwd()
DATA_DIR = f'{PROJECT_DIR}/ext/ext/data'
RESULT_DIR = f'{PROJECT_DIR}/ext/ext/results'
RAW_DATA_DIR = f'{DATA_DIR}/raw'

SERVER_URL = "http://localhost:8080"

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-visible_gpus', default='-1', type=str) # ex) -gpu 0,1,2
	parser.add_argument('-n_cpus', default='2', type=str)
	parser.add_argument('-pt', default='1209_1236/model_step_18000.pt', type=str)

	args = parser.parse_args()	

	ext_summary = ExtSummarization(
		visible_gpus=args.visible_gpus,	# using cpu
		n_cpus=args.n_cpus,
		pt=args.pt
	)
	abs_summary = AbsSummarization()

	model_folder, model_name = args.pt.rsplit('/', 1)
	model_name = model_name.split('_', 1)[1].split('.')[0]
	ext_result = ext_summary.predict(model_folder, model_name)

	for sent in ext_result:
		abs_sum = abs_summary.predict(sent['extractive_sents'])
		body_json = {"link": sent['link'], "summary": abs_sum}
		requests.put(f'{SERVER_URL}/news', json=body_json)
