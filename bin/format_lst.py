#!/usr/bin/python
# -*-coding:utf-8 -*-
"""
predict module
"""
import sys
import os
import json
import random
import hashlib
import logging
from data_recognize import format_one_time_str
# sys.path.append(os.path.abspath('..'))
# from utils import utils


def write_by_lines(path, data, t_code="utf-8"):
    """write the data"""
    print('**************--------:', path)
    with open(path, "w") as outfile:
        [outfile.write(d + "\n") for d in data]
        
    
def md5(s: str):
    """
    md5加密生成32位小写字符串
    :param s:
    :return:
    """
    m = hashlib.md5()
    m.update(s.encode(encoding='utf-8'))
    return m.hexdigest()


def format_test_lst(lst: list):
    """
    将拆分后的字符串列表转成预测需要的格式:
    {text: "***", id:"md5"}
    :param lst 文章拆分的句子列表
    :return res 组成特定格式的字典列表返回
    """
    res = []
    for line in lst:
        if line and line.strip() and len(line.strip()) >= 3:
            dic = dict()
            text = line
            # sid = utils.md5(text)
            sid = md5(text)
            dic["text"] = text
            dic["id"] = sid
            res.append(dic)
    return res


def origin_events_4test(sents):
    """
    origin_events_process
    deal test json data like:{"text": "国际组织IEEE限制华为后，北大教授宣布退出IEEE编委会", "id": "17388c65ef9d77aff12d8cc1f645e41c"}
    转换格式并写入test.json文件
    有数据则正常覆盖写入，没有的话则删除原来存在的文件
    """
    output = []
    for d_json in sents:
        event = {}
        event["trigger"] = ""
        event["trigger_start_index"] = 0
        event["class"] = ""
        event["event_type"] = ""
        event["arguments"] = []
        argument  = {}
        argument["argument_start_index"] = 0
        argument["role"] = ""
        argument["argument"] = ""
        argument["alias"] = []
        event["arguments"].append(argument)
        event["event_id"] = u"{}_{}".format(d_json["id"], "no_event")
        event["text"] = d_json["text"]
        event["id"] = d_json["id"]
        output.append(json.dumps(event, ensure_ascii=False))
    random.shuffle(output)  # 随机一下
    
    print(
        u"include sentences {}, events {}, test datas {}"
            .format(len(sents), len(output), len(output)))
    # pppath = os.path.abspath(os.path.join(os.getcwd(), "../.."))
    # print('***********:', pppath)
    # ***********: /home
    # cwd = os.getcwd()
    # print('***********:', cwd)
    # ***********: /home/zx/DuEE_baseline
    # print('*******************:', os.path.abspath(os.path.dirname(__file__)))
    # *******************: /home/zx/DuEE_baseline/bin
    
    save_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../data')
    # save_dir = r'../data'
    # print('**************--------:', save_dir)
    # **************--------: /home/zx/DuEE_baseline/bin/../data
    target_path = u"{}/test.json".format(save_dir)
    # print(output)
    if output:
        # utils.write_by_lines(target_path, output)
        write_by_lines(target_path, output)
    else:
        if os.path.exists(target_path):
            os.remove(target_path)

        with open(target_path, 'w', encoding='utf-8') as fw:
            pass


def save_test_dict_file(sentences):
    """
    将字符串列表转换两次格式并保存为预测需要的文件格式 test.json
    """
    res = format_test_lst(sentences)
    # save to test.json
    #print('--------------len(res)--', len(res))
    origin_events_4test(res)
    

def read_pred_json_format():
    """
    读取已经预测完成的pred.json文件并格式化为需要的json格式返回给客户端
    """
    save_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../result')
    # print('**************--------:', save_dir)
    # **************--------: /home/zx/DuEE_baseline/bin/../result
    pred_path = u"{}/pred.json".format(save_dir)
    # pred_path = r'../result/pred.json'
    res = []
    if os.path.exists(pred_path):
        with open(pred_path, 'r', encoding='utf-8') as fr:
            for line in fr:
                if line and line.strip():
                    js = json.loads(line.strip())
                    # {"id": "627580dca403c840c3b67f1cd6c784d0", "text": "梅克伦堡-施特雷利茨政府任命弗里德里希·弗朗茨四世为梅克伦堡-施特雷利茨摄政。",
                    # "event_list": [{"trigger": "任命", "event_type": "职位变更-职位", "arguments": [{"role": "职位主体",
                    # "argument": "弗里德里希·弗朗茨四世"}, {"role": "职位客体", "argument": "梅克伦堡-施特雷利茨摄政"}]}]}
                    event_list = js["event_list"]
                    dic = dict()
                    dic["text"] = js["text"]
                    temp = []
                    for e in event_list:
                        event = dict()
                        event["trigger"] = e["trigger"]
                        event_type = e["event_type"]
                        if '-' in event_type:
                            event["event_type"] = event_type.split('-')[0]
                        else:
                            event["event_type"] = event_type
                        arguments = dict()
                        args = e["arguments"]
                        ishaveobj = False
                        for arg in args:
                            role = arg["role"]
                            key = ""
                            value = arg["argument"]
                            if len(value) <= 1:
                                continue
                            if "时间" == role:
                                key = "time"
                                try:
                                    value = format_one_time_str(value)
                                except Exception as e:
                                    print(e)
                            elif "主体" in role:
                                key = "subject"
                            elif "客体" in role:
                                key = "object"
                                ishaveobj = True
                            if key:
                                if key not in arguments:
                                    arguments[key] = [value]
                                else:
                                    arguments[key].append(value)
                        # TODO 2020-10-14 temp change
                        #if ishaveobj:
                        event["arguments"] = arguments
                        temp.append(event)
                    if temp:
                        dic["event_list"] = temp
                        res.append(dic)
    return res
    

