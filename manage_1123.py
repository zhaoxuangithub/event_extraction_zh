"""
flask manage
"""
import os
import sys
import json
import time
import urllib
import copy
from flask import Flask, request, Response
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('./bin/utils'))
print(sys.path)
from bin.utils.split_sentence_tool import split_txt
from format_lst import save_test_dict_file, read_pred_json_format, handle_return_events_4test, read_pred_json_format_1126
from init_trigger import get_trigger_init_dict, re_use_some, re_use_exe
from init_role import get_role_init_dict
from common_args import get_common_args, get_role_args
from predict_trigger import predict_trigger, predict_trigger_1126
from predict_role import predict_role, predict_role_1126
from predict_eval_process import test_data_2_eval, predict_data_2_eval, predict_data_2_eval_1126

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

arg1 = None
rol_args = None
count = 1
trigger_dict = dict()
role_dict = dict()
config_dict = dict()
current_path = os.getcwd()


def get_new_path(ab_path, suf):
    """
    获取新路径，根据时间戳以及500循环数进行文件名调整返回
    """
    old_test_file_name = os.path.basename(ab_path)
    old_test_file_dir = os.path.dirname(ab_path)
    new_test_file_name = old_test_file_name[:-5] + "_" + suf + old_test_file_name[-5:]
    new_file_path = os.path.join(old_test_file_dir, new_test_file_name)
    return new_file_path, new_test_file_name


def delete_temp_file(*lst_args):
    """
    删除对应的多个个临时文件
    """
    for p in lst_args:
        if os.path.exists(p):
            print("+++++++++++++++++++++++++++++", p)
            os.remove(p)
            
            
def delete_temp_dict(d):
    """
    删除字典中指定内容
    """
    del d["reader"]
    del d["startup_prog"]
    del d["test_prog"]
    del d["test_pyreader"]
    
    
def read_config_pro():
    """读取配置文件"""
    global config_dict
    with open(r"./config.proprities", 'r', encoding="utf-8") as fr:
        for line in fr:
            if line and line.strip():
                temp_list = line.strip().split("=")
                config_dict[temp_list[0]] = temp_list[1]
    
    
# @app.route('/event_extraction', methods=['POST'])
# def rel_extract():
#     global count
#     count += 1
#     if count >= 500:
#         count = 1
#     tri_arg = get_common_args(current_path)
#     base_time = str(int(time.time() * (10 ** 7)) + (count % 500))
#     trigger_dict = get_trigger_init_dict(tri_arg, base_time)
#     # test path, test file
#     # test_set, new_name = get_new_path(trigger_dict["args"].test_set, base_time)
#     test_set, new_name = get_new_path(r"./data/test.json", base_time)
#     trigger_dict["args"].test_set = test_set
#     # trigger path, trigger file
#     trigger_new_file_path, trigger_new_file_name = get_new_path(r"./save_model/trigger/pred_trigger.json", base_time)
#     trigger_dict["args"].trigger_pred_save_path = trigger_new_file_path
#     print("+++++++++++++++++++++++++++++++++++++++++++++++++++", test_set)
#     texts = request.json['content']
#     sentences = []
#     for t in texts:
#         sentences.extend(split_txt(t))
#     # 调整格式存储为需要的测试格式文件
#     save_test_dict_file(sentences, new_name)
#
#     # 预测trigger
#     predict_trigger(trigger_dict)
#     # ?????
#     # if 'exe' in trigger_dict:
#     #     del trigger_dict['exe']
#     # 预测role
#     # 先初始化
#     # if not role_dict:
#     rol_args = get_role_args(current_path)
#     role_dict = get_role_init_dict(rol_args, base_time)
#     # 预测
#     role_dict["args"].test_set = test_set
#     # role_new_file_path, role_new_file_name = get_new_path(role_dict["args"].trigger_pred_save_path, base_time)
#     role_new_file_path, role_new_file_name = get_new_path(r"./save_model/role/pred_role.json", base_time)
#     role_dict["args"].trigger_pred_save_path = role_new_file_path
#     predict_role(role_dict)
#     # ???????
#     # if 'exe' in role_dict:
#     #     del role_dict['exe']
#     # TODO 2020-11-23
#     # os.system('sh ./bin/script/predict_data_new.sh')
#     # gold_p = r"./result/gold.json"
#     # gold_new_path, gold_new_name = get_new_path(gold_p, base_time)
#     # test_data_2_eval(test_set, gold_new_path)
#     result_p = r"./result/pred.json"
#     result_new_file_path, result_new_file_name = get_new_path(result_p, base_time)
#     predict_data_2_eval(trigger_new_file_path, role_new_file_path, r"./dict/event_schema.json", result_new_file_path)
#
#     # os.system('sh ./bin/script/predict_data.sh')
#     result_dict = {'content': read_pred_json_format(result_new_file_path)}
#     result_json = json.dumps(result_dict, ensure_ascii=False)
#     # 删除中间文件
#     delete_temp_file(test_set, trigger_new_file_path, role_new_file_path, result_new_file_path)
#     # delete_temp_dict(trigger_dict)
#     # delete_temp_dict(role_dict)
#     del trigger_dict
#     del role_dict
#     return Response(result_json, mimetype='application/json')


def post_event_extraction_role(suf_dic):
    if config_dict:
        url = "http://{0}:{1}/event_extraction_role".format(config_dict["ip"], config_dict["port"])
    else:
        url = "http://0.0.0.0:40000/event_extraction_role"
    data = json.dumps(suf_dic).encode(encoding='utf-8')
    headers = {"Content-Type": 'application/json'}
    req = urllib.request.Request(url=url, headers=headers, data=data)
    try:
        resp = urllib.request.urlopen(req).read()
        resp_dic = json.loads(resp.decode('utf-8'))
        result_json_list = resp_dic["content"]
        return result_json_list
    except Exception as e:
        print(e)
        return list()
    
    
def post_event_extraction_role_1126(suf_dic):
    if config_dict:
        url = "http://{0}:{1}/event_extraction_role".format(config_dict["ip"], config_dict["port"])
    else:
        url = "http://0.0.0.0:40000/event_extraction_role"
    data = json.dumps(suf_dic, ensure_ascii=False).encode(encoding='utf-8')
    headers = {"Content-Type": 'application/json'}
    req = urllib.request.Request(url=url, headers=headers, data=data)
    try:
        resp = urllib.request.urlopen(req).read()
        resp_dic = json.loads(resp.decode('utf-8'))
        result_json_list = resp_dic["content"]
        return result_json_list
    except Exception as e:
        print(e)
        return list()


# first = True
# @app.route('/event_extraction', methods=['POST'])
# def rel_extract():
#     global count, trigger_dict, role_dict, first
#     count += 1
#     if count >= 500:
#         count = 1
#     base_time = str(int(time.time() * (10 ** 7)) + (count % 500))
#     # reader, startup_prog, test_prog, test_pyreader, graph_vars, exe = re_use_some(trigger_dict, base_time)
#     # trigger_dict['reader'] = reader
#     # trigger_dict['startup_prog'] = startup_prog
#     # trigger_dict['exe'] = exe
#     # trigger_dict['test_prog'] = test_prog
#     # trigger_dict['test_pyreader'] = test_pyreader
#     # trigger_dict['graph_vars'] = graph_vars
#     # temp_dict = copy.deepcopy(trigger_dict)
#     if first:
#         first = False
#         temp_dict = trigger_dict
#     else:
#         temp_dict = get_trigger_init_dict(arg1, base_time)
#     # if "exe" in temp_dict:
#     #     del temp_dict["exe"]
#     # exe = re_use_exe(temp_dict)
#     # temp_dict["exe"] = exe
#     test_set, new_name = get_new_path(r"./data/test.json", base_time)
#     temp_dict["args"].test_set = test_set
#     trigger_new_file_path, trigger_new_file_name = get_new_path(r"./save_model/trigger/pred_trigger.json", base_time)
#     temp_dict["args"].trigger_pred_save_path = trigger_new_file_path
#     role_name = r"pred_role_{}.json".format(base_time)
#     pred_name = r"pred_{}.json".format(base_time)
#     pred__path = os.path.join(r"../DuEE_baseline_second/result", pred_name)
#     role_path = os.path.join(r"../DuEE_baseline_second/save_model/role", role_name)
#     print("+++++++++++++++++++++++++++++++++++++++++++++++++++", test_set)
#     try:
#         texts = request.json['content']
#         sentences = []
#         for t in texts:
#             sentences.extend(split_txt(t))
#         # 调整格式存储为需要的测试格式文件
#         save_test_dict_file(sentences, new_name)
#         # 预测trigger
#         predict_trigger(temp_dict)
#         # 获取role
#         res = post_event_extraction_role({"basetime": base_time})
#         print("****************************success*****************")
#         # print(res)
#         delete_temp_file(test_set, trigger_new_file_path, role_path, pred__path)
#         result_json = json.dumps({"content": res}, ensure_ascii=False)
#     except Exception as e:
#         print("*******************error****************************", e)
#         delete_temp_file(test_set, trigger_new_file_path, role_path, pred__path)
#         result_json = json.dumps({"content": []}, ensure_ascii=False)
#     return Response(result_json, mimetype='application/json')


first = False
@app.route('/event_extraction', methods=['POST'])
def rel_extract():
    global count, trigger_dict, role_dict, first, arg1, rol_args
    count += 1
    if count >= 500:
        count = 1
    base_time = str(int(time.time() * (10 ** 7)) + (count % 500))
    if first:
        first = False
        trigger_dict = get_trigger_init_dict(arg1, base_time)
        # role_dict = get_role_init_dict(rol_args, base_time)
    try:
        texts = request.json['content']
        sentences = []
        for t in texts:
            sentences.extend(split_txt(t))
        # 调整格式存储为需要的测试格式文件
        # save_test_dict_file(sentences, new_name)
        # TODO 1126 中间变量返回列表
        test_list = handle_return_events_4test(sentences)
        # 预测trigger
        # predict_trigger(trigger_dict)
        # TODO 1126 中间变量返回列表
        test_trigger_list = predict_trigger_1126(trigger_dict, test_list)
        # 获取role
        # res = post_event_extraction_role({"basetime": base_time})
        # TODO 1126 传递列表进行获取结果
        res = post_event_extraction_role_1126({"test_list": test_list, "test_trigger_list": test_trigger_list, "base_time": base_time})
        
        # # TODO 1126 下午 合并尝试
        # test_role_list = predict_role_1126(role_dict, test_list)
        # outputs = predict_data_2_eval_1126(test_trigger_list, test_role_list, r"./dict/event_schema.json")
        # res = read_pred_json_format_1126(outputs)
        # # TODO 1126 下午 合并尝试
        
        print("****************************success*****************")
        # print(res)
        # TODO 1126 更改后无中间文件不删除
        # delete_temp_file(test_set, trigger_new_file_path, role_path, pred__path)
        result_json = json.dumps({"content": res}, ensure_ascii=False)
        if not res:
            first = True
            # trigger_dict = get_trigger_init_dict(arg1, base_time)
    except Exception as e:
        print("*******************error****************************", e)
        # TODO 1126 更改后无中间文件不删除
        # delete_temp_file(test_set, trigger_new_file_path, role_path, pred__path)
        result_json = json.dumps({"content": []}, ensure_ascii=False)
        # trigger_dict = get_trigger_init_dict(arg1, base_time)
        first = True
    return Response(result_json, mimetype='application/json')


if __name__ == '__main__':
    arg1 = get_common_args(current_path)
    base_time = str(int(time.time() * (10 ** 7)) + 1)
    trigger_dict = get_trigger_init_dict(arg1, base_time)
    # trigger_dict = get_trigger_init_dict(arg1)
    # rol_args = get_role_args(current_path)
    # role_dict = get_role_init_dict(rol_args, base_time)
    # app.run(host='0.0.0.0', port=4444)
    # TODO 2020-11-23
    app.run(host='0.0.0.0', port=39999)
