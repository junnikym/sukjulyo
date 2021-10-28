import os
import json

import torch
import pandas as pd
import numpy as np

from ext.src.make_data import create_json_files

class ExtSummarization():

	def __init__(self, visible_gpus, n_cpus, pt):
		self.PROJECT_DIR = os.getcwd()
		self.RAW_DATA_DIR = f'{self.PROJECT_DIR}/ext/ext/data/raw'
		self.DATA_DIR = f'{self.PROJECT_DIR}/ext/ext/data'
		self.JSON_DATA_DIR = self.DATA_DIR + '/json_data'
		self.BERT_DATA_DIR = self.DATA_DIR + '/bert_data' 
		self.LOG_DIR = f'{self.PROJECT_DIR}/ext/ext/logs'
		self.LOG_PREPO_FILE = self.LOG_DIR + '/preprocessing.log'

		self.MODEL_DIR = f'{self.PROJECT_DIR}/ext/ext/models' 
		self.RESULT_DIR = f'{self.PROJECT_DIR}/ext/ext/results' 

		self.n_cpus=2
		self.visible_gpus=visible_gpus
		self.pt=pt

	def preprocessing(self):
		os.makedirs(self.DATA_DIR, exist_ok=True)
		os.makedirs(self.RAW_DATA_DIR, exist_ok=True)

		# import data
		with open(f'{self.RAW_DATA_DIR}/data.jsonl', 'r') as json_file:
			json_list = list(json_file)

		target_data = []
		for json_str in json_list:
			line = json.loads(json_str)
			target_data.append(line)

		# Convert raw data to df
		df = pd.DataFrame(target_data)
		df['extractive_sents'] = df.apply(lambda row: list(np.array(row['article_original'])) , axis=1)

		target_data_df = pd.DataFrame(target_data)
		
		os.makedirs(self.JSON_DATA_DIR, exist_ok=True)
		os.makedirs(self.BERT_DATA_DIR, exist_ok=True)

		json_data_dir = f"{self.JSON_DATA_DIR}/test"
		if os.path.exists(json_data_dir):
			os.system(f"rm {json_data_dir}/*")
		else:
			os.mkdir(json_data_dir)

		create_json_files(target_data_df, data_type='test', path=self.JSON_DATA_DIR)
		
		## Convert json to bert.pt files
		bert_data_dir = f"{self.BERT_DATA_DIR}/test"
		if os.path.exists(bert_data_dir):
			os.system(f"rm {bert_data_dir}/*")
		else:
			os.mkdir(bert_data_dir)
			
		os.chdir(f'{self.PROJECT_DIR}/ext/src')
		os.system(f"python preprocess.py"
			+ f" -mode format_to_bert -dataset test"
			+ f" -raw_path {json_data_dir}"
			+ f" -save_path {bert_data_dir}"
			+ f" -log_file {self.LOG_PREPO_FILE}"
			+ f" -lower -n_cpus {self.n_cpus}")

	def predict(self, preprocessing):

		if preprocessing:
			self.preprocessing()

		model_folder, model_name = self.pt.rsplit('/', 1)
		model_name = model_name.split('_', 1)[1].split('.')[0]

		os.chdir(f'{self.PROJECT_DIR}/ext/src')
		os.system(f"""\
				python3 train.py -task ext -mode test \
				-test_from {self.MODEL_DIR}/{self.pt} \
				-bert_data_path {self.BERT_DATA_DIR}/test \
				-result_path {self.RESULT_DIR}/result_{model_folder} \
				-log_file {self.LOG_DIR}/test_{model_folder}.log \
				-test_batch_size 1  -batch_size 000 \
				-sep_optim true -use_interval true -visible_gpus {self.visible_gpus} \
				-max_pos 512 -max_length 200 -alpha 0.95 -min_length 50 \
				-report_rouge False \
				-max_tgt_len 100
			""")