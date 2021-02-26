"""
split sentences
"""
import re


def switch_dq_and(txt):
	"""
	将双引号中的句子换成为&& 防止拆分句子时出现问题
	并返回提取后的句子列表和替换后的文本
	:param txt:
	:param sents: 替换的源双引号句子列表
	:return:
	"""
	txt = txt.replace(r'“”', "")
	txt = txt.replace(r'""', "")
	sents = []
	while '“' in txt and '”' in txt:
		s = txt.find('“')
		e = txt.find('”')
		if s < e:
			e += 1
			se = txt[s:e]
			# print(se)
			sents.append(se)
			txt = txt.replace(se, '&&', 1)
			# print(txt)
		else:
			break
	return txt, sents


def cut_sent(para):
	"""中文 re 分句"""
	para = re.sub('([。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
	para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
	para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
	para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
	# 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
	para = para.rstrip()  # 段尾如果有多余的\n就去掉它
	# 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
	return para.split("\n")


def reduction_sentences(dqs, sentences):
	"""
	根据之前提取出的字符串列表和切分后的句子列表根据特殊符号&进行句子还原
	:param dqs: 提取的双引号句子列表
	:param sentences: 句子拆分结果列表
	:return:
	"""
	ressents = []
	index = 0
	for s in sentences:
		temp = s
		while '&&' in temp and index < len(dqs):
			temp = temp.replace('&&', dqs[index], 1)
			index += 1
		ressents.append(temp)
	return ressents


def split_txt(txt: str):
	"""
	长文本分句进行句子拆分并返回拆分后的句子列表
	"""
	# 替换并提取双引号句子
	txt, dquos = switch_dq_and(txt)
	# 对处理后的文本进行分句
	# re 分句
	temps = cut_sent(txt)
	# 将分句后的结果再将占位符替换回原来的双引号句子便于后续处理
	if dquos:
		sentences = reduction_sentences(dquos, temps)
	else:
		sentences = temps
	return sentences


if __name__ == '__main__':
	txt = "国际金融中心（英语：Financial centre），指以第三级产业经济为主；以金融业服务业为中心的全球城市，" \
	      "这个全球城市必须拥有跨国公司和国际大银行的总部设立，要有活跃的外汇市场、股票市场、期货交易、证券市场等金融产品市场，" \
	      "并拥有至少一个证券交易所。此外，还需要完善的法律制度和资本主义环境，并有著健全的交通运输、人才教育等硬件建设与体系制度。\n" \
	      "截至2018年9月12日，全球金融中心指数排名为[1]：\n\n\n\n。习主席说：“加强共产党领导，一党专政，多党合作。”，提高共产党领导能力。"
	res = split_txt(txt)
	print(res)
	# ['国际金融中心（英语：Financial centre），指以第三级产业经济为主；以金融业服务业为中心的全球城市，这个全球城市必须拥有跨国公司和国际大银行的总部设立，要有活跃的外汇市场、股票市场、期货交易、证券市场等金融产品市场，并拥有至少一个证券交易所。',
	# '此外，还需要完善的法律制度和资本主义环境，并有著健全的交通运输、人才教育等硬件建设与体系制度。',
	# '', '截至2018年9月12日，全球金融中心指数排名为[1]：', '', '', '', '。', '习主席说：“加强共产党领导，一党专政，多党合作。”，提高共产党领导能力。']

