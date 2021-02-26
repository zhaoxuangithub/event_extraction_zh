"""
测试代码,处理数据使用
"""
import os


def change_filename_pred(fpath, tpath):
	totalnames = os.listdir(fpath)
	# if 'test_temp.json' in totalnames:
	# 	os.remove(os.path.join(fpath, 'test_temp.json'))
	temp_filename = os.path.join(fpath, 'test_temp.json')
	ta_temp_filename = os.path.join(tpath, 'pred.json')
	# print('-------------------------------------', temp_filename)
	# print('-------------------------------------', ta_temp_filename)
	tastartnames = [name for name in totalnames if name.startswith('wiki')]
	# print('-------------------------------------', tastartnames)
	for name in tastartnames:
		print('-------------------------------------', name)
		if os.path.exists(temp_filename):
			os.remove(temp_filename)
		filename = os.path.join(fpath, name)
		os.rename(filename, temp_filename)
		if os.path.exists(ta_temp_filename):
			os.remove(ta_temp_filename)
		# 开始预测
		os.system('sh ./bin/script/train_and_eval4test.sh')
		# 预测后,修改对应pred.json 为 name.json
		if os.path.exists(ta_temp_filename):
			pred_name = name[:-4] + '.json'
			os.rename(ta_temp_filename, os.path.join(tpath, pred_name))
			print('%s was pred success' % os.path.join(tpath, pred_name))
		

if __name__ == '__main__':
	# test change filename
	# na1 = r'D:/Pycharm_workspace/DuEE_baseline/test1.txt'
	# na2 = r'D:/Pycharm_workspace/DuEE_baseline/test2.txt'
	# os.rename(na1, na2)
	current_path = os.getcwd()
	p1 = os.path.join(current_path, 'data')
	p2 = os.path.join(current_path, 'result')
	change_filename_pred(p1, p2)
