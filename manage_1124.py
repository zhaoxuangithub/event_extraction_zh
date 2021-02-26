"""
flask manage
"""
import os
import sys
import json
import time
from flask import Flask, request, Response
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('./bin/utils'))
print(sys.path)
from bin.utils.split_sentence_tool import split_txt
from format_lst import save_test_dict_file, read_pred_json_format, read_pred_json_format_1126
from init_trigger import get_trigger_init_dict
from init_role import get_role_init_dict, re_use_some, re_use_exe
from common_args import get_common_args, get_role_args
from predict_trigger import predict_trigger
from predict_role import predict_role, predict_role_1126
from predict_eval_process import test_data_2_eval, predict_data_2_eval, predict_data_2_eval_1126

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

rol_args = None
role_dict = dict()
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
    
    
# first = True
# @app.route('/event_extraction_role', methods=['POST'])
# def rel_extract_role():
#     global role_dict, rol_args, first
#     test_set = ""
#     tri_set = ""
#     result_new_file_path = ""
#     role_new_file_path = ""
#     try:
#         base_time = request.json['basetime']
#         # del role_dict["exe"]
#         # reader, startup_prog, test_prog, test_pyreader, graph_vars, exe = re_use_some(role_dict, base_time)
#         # role_dict['reader'] = reader
#         # role_dict['startup_prog'] = startup_prog
#         # role_dict['exe'] = exe
#         # role_dict['test_prog'] = test_prog
#         # role_dict['test_pyreader'] = test_pyreader
#         # role_dict['graph_vars'] = graph_vars
#         # exe = re_use_exe(role_dict)
#         # role_dict['exe'] = exe
#         if first:
#             first = False
#             temp_dict = role_dict
#         else:
#             temp_dict = get_role_init_dict(rol_args, base_time)
#         test_name = "test_{}.json".format(base_time)
#         tri_name = "pred_trigger_{}.json".format(base_time)
#         test_set = os.path.join(r"../DuEE_baseline/data", test_name)
#         tri_set = os.path.join(r"../DuEE_baseline/save_model/trigger", tri_name)
#         temp_dict["args"].test_set = test_set
#         role_new_file_path, role_new_file_name = get_new_path(r"./save_model/role/pred_role.json", base_time)
#         temp_dict["args"].trigger_pred_save_path = role_new_file_path
#         print("+++++++++++++++++++++++++++++++++++++++++++++++++++", test_set)
#         # 预测role
#         predict_role(temp_dict)
#         # TODO 2020-11-23
#         # os.system('sh ./bin/script/predict_data_new.sh')
#         # gold_p = r"./result/gold.json"
#         # gold_new_path, gold_new_name = get_new_path(gold_p, base_time)
#         # test_data_2_eval(test_set, gold_new_path)
#         result_p = r"./result/pred.json"
#         result_new_file_path, result_new_file_name = get_new_path(result_p, base_time)
#         predict_data_2_eval(tri_set, role_new_file_path, r"./dict/event_schema.json", result_new_file_path)
#
#         result_dict = {'content': read_pred_json_format(result_new_file_path)}
#         result_json = json.dumps(result_dict, ensure_ascii=False)
#         # 删除中间文件
#         delete_temp_file(test_set, tri_set, role_new_file_path, result_new_file_path)
#     except Exception as e:
#         print(e)
#         result_json = json.dumps({"content": []}, ensure_ascii=False)
#         # 删除中间文件
#         delete_temp_file(test_set, tri_set, role_new_file_path, result_new_file_path)
#     return Response(result_json, mimetype='application/json')


# first = False
# @app.route('/event_extraction_role', methods=['POST'])
# def rel_extract_role():
#     global role_dict, rol_args, first
#     test_set = ""
#     tri_set = ""
#     result_new_file_path = ""
#     role_new_file_path = ""
#     try:
#         base_time = request.json['basetime']
#         # del role_dict["exe"]
#         # reader, startup_prog, test_prog, test_pyreader, graph_vars, exe = re_use_some(role_dict, base_time)
#         # role_dict['reader'] = reader
#         # role_dict['startup_prog'] = startup_prog
#         # role_dict['exe'] = exe
#         # role_dict['test_prog'] = test_prog
#         # role_dict['test_pyreader'] = test_pyreader
#         # role_dict['graph_vars'] = graph_vars
#         # exe = re_use_exe(role_dict)
#         # role_dict['exe'] = exe
#         if first:
#             first = False
#             role_dict = get_role_init_dict(rol_args, base_time)
#         test_name = "test_{}.json".format(base_time)
#         tri_name = "pred_trigger_{}.json".format(base_time)
#         test_set = os.path.join(r"../DuEE_baseline/data", test_name)
#         tri_set = os.path.join(r"../DuEE_baseline/save_model/trigger", tri_name)
#         role_dict["args"].test_set = test_set
#         role_new_file_path, role_new_file_name = get_new_path(r"./save_model/role/pred_role.json", base_time)
#         role_dict["args"].trigger_pred_save_path = role_new_file_path
#         print("+++++++++++++++++++++++++++++++++++++++++++++++++++", test_set)
#         # 预测role
#         predict_role(role_dict)
#         # TODO 2020-11-23
#         # os.system('sh ./bin/script/predict_data_new.sh')
#         # gold_p = r"./result/gold.json"
#         # gold_new_path, gold_new_name = get_new_path(gold_p, base_time)
#         # test_data_2_eval(test_set, gold_new_path)
#         result_p = r"./result/pred.json"
#         result_new_file_path, result_new_file_name = get_new_path(result_p, base_time)
#         predict_data_2_eval(tri_set, role_new_file_path, r"./dict/event_schema.json", result_new_file_path)
#
#         res = read_pred_json_format(result_new_file_path)
#         result_json = json.dumps({'content': res}, ensure_ascii=False)
#         # 删除中间文件
#         delete_temp_file(test_set, tri_set, role_new_file_path, result_new_file_path)
#         if not res:
#             first = True
#             # role_dict = get_role_init_dict(rol_args, base_time)
#     except Exception as e:
#         print(e)
#         result_json = json.dumps({"content": []}, ensure_ascii=False)
#         # 删除中间文件
#         delete_temp_file(test_set, tri_set, role_new_file_path, result_new_file_path)
#         # role_dict = get_role_init_dict(rol_args, base_time)
#         first = True
#     return Response(result_json, mimetype='application/json')


# TODO 1126 版本不使用中间文件处理
first = False
@app.route('/event_extraction_role', methods=['POST'])
def rel_extract_role():
    global role_dict, rol_args, first
    test_set = ""
    tri_set = ""
    result_new_file_path = ""
    role_new_file_path = ""
    try:
        base_time = request.json['base_time']
        # TODO 1126 传递中间结果列表，代替文件处理
        test_list = request.json["test_list"]
        # print("+++++++++++++++++++++++++++type(test_list)", type(test_list))
        test_trigger_list = request.json["test_trigger_list"]
        if first:
            first = False
            role_dict = get_role_init_dict(rol_args, base_time)
        # test_name = "test_{}.json".format(base_time)
        # tri_name = "pred_trigger_{}.json".format(base_time)
        # test_set = os.path.join(r"../DuEE_baseline/data", test_name)
        # tri_set = os.path.join(r"../DuEE_baseline/save_model/trigger", tri_name)
        # role_dict["args"].test_set = test_set
        # role_new_file_path, role_new_file_name = get_new_path(r"./save_model/role/pred_role.json", base_time)
        # role_dict["args"].trigger_pred_save_path = role_new_file_path
        # print("+++++++++++++++++++++++++++++++++++++++++++++++++++", test_set)
        # 预测role
        # predict_role(role_dict)
        # TODO 1126 不使用文件
        # predict_role(role_dict)
        # TODO 1126 预测role不再保存文件
        test_role_list = predict_role_1126(role_dict, test_list)
        # TODO 2020-11-23
        # os.system('sh ./bin/script/predict_data_new.sh')
        # gold_p = r"./result/gold.json"
        # gold_new_path, gold_new_name = get_new_path(gold_p, base_time)
        # test_data_2_eval(test_set, gold_new_path)
        result_p = r"./result/pred.json"
        result_new_file_path, result_new_file_name = get_new_path(result_p, base_time)
        # predict_data_2_eval(tri_set, role_new_file_path, r"./dict/event_schema.json", result_new_file_path)
        # TODO 1126 传递列表参数进行预测结果并返回列表
        # predict_data_2_eval(tri_set, role_new_file_path, r"./dict/event_schema.json", result_new_file_path)
        outputs = predict_data_2_eval_1126(test_trigger_list, test_role_list, r"./dict/event_schema.json")

        # res = read_pred_json_format(result_new_file_path)
        # TODO 不使用中间文件pred.json
        res = read_pred_json_format_1126(outputs)
        result_json = json.dumps({'content': res}, ensure_ascii=False)
        # 删除中间文件
        # delete_temp_file(test_set, tri_set, role_new_file_path, result_new_file_path)
        if not res:
            first = True
            # role_dict = get_role_init_dict(rol_args, base_time)
    except Exception as e:
        print(e)
        result_json = json.dumps({"content": []}, ensure_ascii=False)
        # 删除中间文件
        # delete_temp_file(test_set, tri_set, role_new_file_path, result_new_file_path)
        # role_dict = get_role_init_dict(rol_args, base_time)
        first = True
    return Response(result_json, mimetype='application/json')


if __name__ == '__main__':
    # TODO /home/zx/DuEE_baseline_second/bin
    base_time = str(int(time.time() * (10 ** 7)) + 1)
    rol_args = get_role_args(current_path)
    role_dict = get_role_init_dict(rol_args, base_time)
    # TODO 2020-11-24
    app.run(host='0.0.0.0', port=40000)
