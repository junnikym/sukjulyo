from rss_parser import RssParser
from ner import NER

rss_parser = RssParser()
ner = NER()

result = rss_parser.extraction()
for article in result:
	text = f"{article['title']}\n{article['description']}"
	list_of_ner_word, decoding_ner_sentence = ner.predict(text)
	
	print(list_of_ner_word)
	print("\n\n")
