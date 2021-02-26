#!/usr/bin/python
# -*-coding:utf-8 -*-
"""
@File    : my_pri_test0108.py
@Date    : 2021-01-08 15:37
@Author  : ZX
测试代码，用于临时调试使用
"""
import os
import json


def format_eet_events_file(p):
	res = []
	with open(p, 'r', encoding="utf-8") as fr:
		for line in fr:
			if line and line.strip():
				d = json.loads(line.strip())
				"""
				{"text": "4月2日，蔡元培和吴稚晖、李石曾、张静江、古应芬、陈果夫、李宗仁、黄绍竑等8人在上海召开所谓中央监察委员会全体会议(全体监察委员20人，仅到8人，不过半数)，蔡元培任主席，讨论清除中国共产党的行动。",
				"id": "b58ed1f77ebadc37bede75ab8fa5b326", "event_list": [{"event_type": "会议活动", "trigger": "召开", "trigger_start_index": 42,
				"arguments": [{"argument_start_index": 0, "role": "时间", "argument": "4月2日", "alias": []},
				{"role": "会议活动主体", "argument_start_index": 5, "argument": "蔡元培", "alias": []},
				{"role": "会议活动主体", "argument_start_index": 9, "argument": "吴稚晖", "alias": []},
				{"role": "会议活动主体", "argument_start_index": 13, "argument": "李石曾", "alias": []},
				{"role": "会议活动主体", "argument_start_index": 17, "argument": "张静江", "alias": []},
				{"role": "会议活动主体", "argument_start_index": 21, "argument": "古应芬", "alias": []},
				{"role": "会议活动主体", "argument_start_index": 25, "argument": "陈果夫", "alias": []},
				{"role": "会议活动主体", "argument_start_index": 29, "argument": "李宗仁", "alias": []},
				{"role": "会议活动主体", "argument_start_index": 33, "argument": "黄绍竑", "alias": []},
				{"role": "会议活动客体", "argument_start_index": 46, "argument": "中央监察委员会全体会议", "alias": []}],
				"class": "会议活动"}]}
				"""
				if "event_list" in d:
					event_list = d["event_list"]
					if len(event_list) > 0:
						for e in event_list:
							e["event_type"] = "综合"
							e["class"] = "综合"
							if "arguments" in e:
								arguments = e["arguments"]
								if len(arguments) > 0:
									for arg in arguments:
										role = arg["role"]
										if "主体" in role:
											arg["role"] = "主体"
										elif "客体" in role:
											arg["role"] = "客体"
									e["arguments"] = arguments
						d["event_list"] = event_list
				res.append(d)
	p = p[:-5] + "_1" + p[-5:]
	with open(p, 'w', encoding="utf-8") as fw:
		for d in res:
			fw.write(json.dumps(d, ensure_ascii=False) + "\n")
			
			
if __name__ == "__main__":
	p1 = r"data_0108/eet_events.json"
	format_eet_events_file(p1)

