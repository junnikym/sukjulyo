import json

JSON_FILE_PATH 	= './rss.json'
MD_FILE_PATH 	= './rss.md'

url_md_file = open(MD_FILE_PATH, 'r')

url_list = []

while True:
	line = url_md_file.readline()
	if not line:
		break;

	if line[0] == '[' and line[-6: -1] == "<br/>":
		elem = {'corp': None, 'cate': None, 'url': None}

		corp_sep_i = line.find('-')
		cate_sep_i = line.find(']')
		url_sep_open_i = line.find('(')
		url_sep_close_i = line.find(')')

		if url_sep_open_i == -1 or url_sep_close_i == -1:
			print("WARNING : NO URL")

		elem['corp'] = line[1:(cate_sep_i if corp_sep_i == -1 else corp_sep_i)]
		if(corp_sep_i != -1):
			elem['cate'] = line[corp_sep_i+1: cate_sep_i]
		
		elem['url'] = line[url_sep_open_i+1: url_sep_close_i]

		url_list.append(elem);

url_md_file.close()

with open(JSON_FILE_PATH, 'w') as out_f:
    json.dump(url_list, out_f)