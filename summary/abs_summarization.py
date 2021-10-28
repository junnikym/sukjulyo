import torch
from transformers import PreTrainedTokenizerFast
from transformers import BartForConditionalGeneration

class AbsSummarization():

	def __init__(self):
		self.tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-summarization')
		self.model = BartForConditionalGeneration.from_pretrained('gogamza/kobart-summarization')

	def predict(self, text):
		raw_input_ids = self.tokenizer.encode(text)
		input_ids = [self.tokenizer.bos_token_id] + raw_input_ids + [self.tokenizer.eos_token_id]

		summary_ids = self.model.generate(torch.tensor([input_ids]))
		return self.tokenizer.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)

abs_summary = AbsSummarization()