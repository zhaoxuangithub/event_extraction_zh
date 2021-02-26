"""
flask manage
"""
import os
import sys
import json
import urllib
from flask import Flask, request, Response
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('./bin/utils'))
print(sys.path)
from bin.utils.split_sentence_tool import split_txt
from format_lst import save_test_dict_file, read_pred_json_format
from init_trigger import get_trigger_init_dict
from init_role import get_role_init_dict
from common_args import get_common_args, get_role_args
from predict_trigger import predict_trigger
from predict_role import predict_role

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

trigger_dict = dict()
role_dict = dict()
current_path = os.getcwd()
config_dict = dict()


def read_config_property():
    """读取配置文件"""
    global config_dict
    config_file_path = r"./config"
    if os.path.exists(config_file_path):
        with open(r"./config", 'r', encoding="utf-8") as fr:
            for line in fr:
                if line and line.strip():
                    line = line.strip()
                    if "=" in line:
                        temp_list = line.split("=")
                        config_dict[temp_list[0]] = temp_list[1]
    else:
        print("{} file is not exists...".format(config_file_path))


def reformat_temp_data(dic_cs, temp_lst):
    """根据事件识别和事件抽取结合格式化最终结果"""
    if temp_lst:
        for d in temp_lst:
            text = d["text"]
            event_list = d["event_list"]
            if event_list:
                for e in event_list:
                    event_type = e["event_type"]
                    if event_type == "综合":
                        e["event_type"] = dic_cs[text]
        return temp_lst
    else:
        return []


def post_entity_dist(url, content_texts):
    data = json.dumps(content_texts).encode(encoding='utf-8')
    # data = bytes(data, 'utf8')
    # print(data)
    headers = {"Content-Type": 'application/json'}
    req = urllib.request.Request(url=url, headers=headers, data=data)
    try:
        resp = urllib.request.urlopen(req).read()
        resp_dic = json.loads(resp.decode('utf-8'))
        return resp_dic
    except Exception as e:
        print(e)
        return []


def event_classify_zh(ts):
    """
    中文事件识别接口访问
    :param ts:
    :return:
    """
    if config_dict:
        event_classify_zh_url = "http://{0}:{1}/event_dist_zh".format(config_dict["zh_event_classify_ip"],
                                                                      config_dict["zh_event_classify_port"])
    else:
        read_config_property()
        if config_dict:
            event_classify_zh_url = "http://{0}:{1}/event_dist_zh".format(config_dict["zh_event_classify_ip"],
                                                                          config_dict["zh_event_classify_port"])
        else:
            event_classify_zh_url = "http://0.0.0.0:4446/event_dist_zh"
    pred_list = post_entity_dist(event_classify_zh_url, {"content": ts})
    return pred_list


# @app.route('/event_extraction', methods=['POST'])
# def rel_extract_0128_cp():
#     global role_dict, is_first
#     texts = request.json['content']
#     sentences = []
#     for t in texts:
#         sentences.extend(split_txt(t))
#     # 调整格式存储为需要的测试格式文件
#     save_test_dict_file(sentences)
#
#     # 预测trigger
#     predict_trigger(trigger_dict)
#     if 'exe' in trigger_dict:
#         del trigger_dict['exe']
#     # 预测role
#     # 先初始化
#     if not role_dict:
#         args = get_role_args(current_path)
#         role_dict = get_role_init_dict(args)
#     # 预测
#     predict_role(role_dict)
#     if 'exe' in role_dict:
#         del role_dict['exe']
#     os.system('sh ./bin/script/predict_data_new.sh')
#
#     # os.system('sh ./bin/script/predict_data.sh')
#     result_dict = {'content': read_pred_json_format()}
#     result_json = json.dumps(result_dict, ensure_ascii=False)
#
#     return Response(result_json, mimetype='application/json')


@app.route('/event_extraction', methods=['POST'])
def rel_extract():
    global role_dict, is_first
    texts = request.json['content']
    if texts:
        pre_lst = event_classify_zh(texts)
        if pre_lst:
            # TODO 0109
            cls_dic = {d["content"]: d["class"] for d in pre_lst}
            sentences = [d["content"] for d in pre_lst]
            # 调整格式存储为需要的测试格式文件
            save_test_dict_file(sentences)
        
            # 预测trigger
            predict_trigger(trigger_dict)
            if 'exe' in trigger_dict:
                del trigger_dict['exe']
            # 预测role
            # 先初始化
            if not role_dict:
                args = get_role_args(current_path)
                role_dict = get_role_init_dict(args)
            # 预测
            predict_role(role_dict)
            if 'exe' in role_dict:
                del role_dict['exe']
            os.system('sh ./bin/script/predict_data_new.sh')
            extrac_pre = read_pred_json_format()
            result_list = reformat_temp_data(cls_dic, extrac_pre)
            result_dict = {'content': result_list}
        else:
            result_dict = {'content': []}
    else:
        result_dict = {'content': []}
    # os.system('sh ./bin/script/predict_data.sh')
    # result_dict = {'content': read_pred_json_format()}
    result_json = json.dumps(result_dict, ensure_ascii=False)
    
    return Response(result_json, mimetype='application/json')


if __name__ == '__main__':
    arg1 = get_common_args(current_path)
    trigger_dict = get_trigger_init_dict(arg1)
    # 初始化读取配置文件
    read_config_property()
    # old
    app.run(host='0.0.0.0', port=4444)
    # TODO 0109
    # app.run(host='0.0.0.0', port=39999)
