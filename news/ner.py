# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
import json
import pickle
import argparse
import torch

from gluonnlp.data import SentencepieceTokenizer
from pathlib import Path

import sys
sys.path.append('./ner')

from model.net import KobertCRF
from data_utils.utils import Config
from data_utils.vocab_tokenizer import Tokenizer
from data_utils.pad_sequence import keras_pad_fn

from inference import DecoderFromNamedEntitySequence

class NER:

	def __init__(
		self,
		model_dir='./ner/experiments/base_model_with_crf_val'
	) -> None:
		model_dir = Path(model_dir)
		model_config = Config(json_path=model_dir / 'config.json')

		# Vocab & Tokenizer
		tok_path = "./ner/ptr_lm_model/tokenizer_78b3253a26.model"
		ptr_tokenizer = SentencepieceTokenizer(tok_path)

		# load vocab & tokenizer
		with open(model_dir / "vocab.pkl", 'rb') as f:
			vocab = pickle.load(f)

		self.tokenizer = Tokenizer(vocab=vocab, split_fn=ptr_tokenizer, pad_fn=keras_pad_fn, maxlen=model_config.maxlen)

		# load ner_to_index.json
		with open(model_dir / "ner_to_index.json", 'rb') as f:
			ner_to_index = json.load(f)
			index_to_ner = {v: k for k, v in ner_to_index.items()}

		# Model
		self.model = KobertCRF(config=model_config, num_classes=len(ner_to_index), vocab=vocab)

		# load
		model_dict = self.model.state_dict()
		
		checkpoint = torch.load(
			"./ner/experiments/base_model_with_crf_val/best-epoch-12-step-1000-acc-0.960.bin", 
			map_location=torch.device('cpu')
		)

		convert_keys = {}
		for k, v in checkpoint['model_state_dict'].items():
			new_key_name = k.replace("module.", '')
			if new_key_name not in model_dict:
				print("{} is not int model_dict".format(new_key_name))
				continue
			convert_keys[new_key_name] = v

		self.model.load_state_dict(convert_keys, strict=False)
		self.model.eval()
		device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

		self.model.to(device)

		self.decoder_from_res = DecoderFromNamedEntitySequence(tokenizer=self.tokenizer, index_to_ner=index_to_ner)

	def predict(self, input_text):
		list_of_input_ids = self.tokenizer.list_of_string_to_list_of_cls_sep_token_ids([input_text])
		x_input = torch.tensor(list_of_input_ids).long()

		## for bert crf
		list_of_pred_ids = self.model(x_input)

		return self.decoder_from_res(
			list_of_input_ids=list_of_input_ids, 
			list_of_pred_ids=list_of_pred_ids
		)


input_text = "그룹 블랙핑크가 뮤직비디오로 또 한번 새로운 기록을 세웠다. 8일(한국시간) 유튜브 측에 따르면 블랙핑크의 '킬 디스 러브' 뮤직비디오는 지난 5일 0시 공개된 이후 24시간 만에 5670만 조회수를 기록했다. 이는 세계적인 팝스타들의 기존 기록을 넘어선 수치다. 더불어 블랙핑크가 지난해 6월 발표했던 '뚜두뚜두(DDU-DU DDU-DU)' 뮤직비디오는 해당 분야 6위에 올랐다. '킬 디스 러브' 뮤직비디오는 공개 2일 14시간 만에 유튜브 1억뷰를 돌파해 세계 신기록을 갈아 치웠고, 현재도 무섭게 상승세를 타고 있다. 음원 또한 발매 직후 미국을 비롯한 전세계 37개 지역 아이튠즈 송차트 1위를 달성하며 인기를 얻고 있다. 미국 아이튠즈 송차트에서는 한국 걸그룹 최초로 1위에 오르는 의미 있는 기록을 세우기도 했다. 또 스포티파이에서는 글로벌 톱50 차트 4위, 미국 톱50 차트 35위에 올랐다. 스포티파이는 1억9700만 사용자에 달하는 현존 스트리밍 서비스 중 가장 많은 회원을 보유하고 있는 파급력 높은 음원 스트리밍 플랫폼으로 꼽힌다. 지난 주말 국내 음악 방송에 출연해 첫 라이브 무대를 펼친 블랙핑크는 오는 12일, 19일 K팝 아이돌 그룹 최초로 미국 최대 음악 축제인 '코첼라 페스티벌' 무대에 오른다. 이를 위해 블랙핑크는 이번주 미국으로 출발할 예정이며, 17일부터 로스엔젤레스를 시작으로 6개 도시 8회 공연으로 이어지는 북미 투어와 함께 현지 유명 TV 방송 및 라디오에 출연해 현지 팬들과 만난다."

ner = NER()
list_of_ner_word, decoding_ner_sentence = ner.predict(input_text)
print('\n\n\n\n')
print(list_of_ner_word)