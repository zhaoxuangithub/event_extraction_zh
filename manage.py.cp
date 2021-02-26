"""
flask manage
"""
import os
import sys
import json
from flask import Flask, request, Response
sys.path.append(os.path.abspath('.'))
from utils.split_sentence_tool import split_txt
from format_lst import save_test_dict_file, read_pred_json_format
from init_trigger import get_trigger_init_dict
from init_role import get_role_init_dict
from common_args import get_common_args, format2_role_args, get_role_args
from predict_trigger import predict_trigger
from predict_role import predict_role

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

trigger_dict = dict()
role_dict = dict()
current_path = os.getcwd()


@app.route('/event_extraction', methods=['POST'])
def rel_extract():
    global trigger_dict, role_dict
    texts = request.json['content']
    sentences = []
    for t in texts:
        sentences.extend(split_txt(t))
    # 调整格式存储为需要的测试格式文件
    save_test_dict_file(sentences)
    # 预测trigger
    # os.system('sh ./bin/script/init_export_path.sh')
    if not trigger_dict:
        arg1 = get_common_args(current_path)
        trigger_dict = get_trigger_init_dict(arg1)
    predict_trigger(trigger_dict)
    # 预测role
    # os.system('sh ./bin/script/init_export_path.sh')
    # 先初始化
    args = get_role_args(current_path)
    role_dict = get_role_init_dict(args)
    # 预测
    predict_role(role_dict)
    os.system('sh ./bin/script/predict_data_new.sh')
    # os.popen('./bin/script/predict_data.sh')
    result_dict = {'content': read_pred_json_format()}
    result_json = json.dumps(result_dict, ensure_ascii=False)
    trigger_dict = dict()
    role_dict = dict()
    return Response(result_json, mimetype='application/json')


if __name__ == '__main__':
    # os.system('sh ./bin/script/init_export_path.sh')
    arg1 = get_common_args(current_path)
    trigger_dict = get_trigger_init_dict(arg1)
    # print(len(trigger_dict))
    # os.system('sh ./bin/script/init_export_path.sh')
    # arg2 = format2_role_args(arg1, pa)
    # role_dict = get_role_init_dict(arg2)
    # print(len(role_dict))
    app.run(host='0.0.0.0', port=39999)
