import os
import argparse
import json

from ext_summarization import ExtSummarization
from abs_summarization import AbsSummarization

PROJECT_DIR = os.getcwd()
DATA_DIR = f'{PROJECT_DIR}/ext/ext/data'
RESULT_DIR = f'{PROJECT_DIR}/ext/ext/results'
RAW_DATA_DIR = f'{DATA_DIR}/raw'
RAW_DATA_DIR = f'{DATA_DIR}/raw'

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-visible_gpus', default='-1', type=str) # ex) -gpu 0,1,2
	parser.add_argument('-n_cpus', default='2', type=str)
	parser.add_argument('-pt', default='1209_1236/model_step_18000.pt', type=str)
	parser.add_argument('-preprocessing', default=False, type=bool)

	args = parser.parse_args()	

	ext_summary = ExtSummarization(
		visible_gpus=args.visible_gpus,	# using cpu
		n_cpus=args.n_cpus,
		pt=args.pt
	)
	abs_summary = AbsSummarization()

	ext_summary.predict(args.preprocessing)

	model_folder, model_name = args.pt.rsplit('/', 1)
	model_name = model_name.split('_', 1)[1].split('.')[0]
	ext_result_file = f'{RESULT_DIR}/result_{model_folder}_{model_name}.candidate'

	save_file = open(ext_result_file, 'r')
	for t in save_file.readlines():
		index_list 	= t.rfind('[')
		
		text 		= t[:index_list]
		index_list 	= t[index_list:]
		
		text 		= text.replace('<q>', ' ')

		print(abs_summary.predict(text))

	save_file.close()
