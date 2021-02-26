# coding: utf-8
#   Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Finetuning on classification tasks."""

from __future__ import absolute_import
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import six
import json
import paddle.fluid as fluid
# sys.path.append(os.path.abspath('..'))
from utils.init import init_checkpoint
from finetune.sequence_label import predict
from utils import utils

    
def predict_trigger(trigger_dict):
    """
    trigger predict
    """
    log = trigger_dict['log']
    args = trigger_dict['args']
    labels_map = trigger_dict['labels_map']
    ernie_config = trigger_dict['ernie_config']
    place = trigger_dict['place']
    dev_count = trigger_dict['dev_count']
    reader = trigger_dict['reader']
    startup_prog = trigger_dict['startup_prog']
    test_prog = trigger_dict['test_prog']
    test_pyreader = trigger_dict['test_pyreader']
    graph_vars = trigger_dict['graph_vars']
    nccl2_num_trainers = trigger_dict['nccl2_num_trainers']
    nccl2_trainer_id = trigger_dict['nccl2_trainer_id']
    if 'exe' in trigger_dict:
        exe = trigger_dict['exe']
    else:
        exe = None
    trigger_pred_save_path = args.trigger_pred_save_path
    if os.path.exists(trigger_pred_save_path):
        print('delete old file : %s' % trigger_pred_save_path)
        os.remove(trigger_pred_save_path)
   
    if args.do_test:
        # TODO 2020-11-24
        # TODO 2021-01-20 取消if not exe --  use_fp16=args.use_fp16) del exe
        if not exe:
            exe = fluid.Executor(place)
            exe.run(startup_prog)

            if args.do_val or args.do_test:
                if not args.init_checkpoint:
                    raise ValueError("args 'init_checkpoint' should be set if"
                                     "only doing validation or testing!")
                init_checkpoint(
                    exe,
                    args.init_checkpoint,
                    main_program=startup_prog,
                    use_fp16=args.use_fp16)
                
        log.error("********************** trigger predict begin **********************")
        test_ret = predict_wrapper(args, reader, exe, test_prog, test_pyreader,
                                   graph_vars, 1, 'final')
        utils.write_by_lines(args.trigger_pred_save_path, test_ret)
        del exe


def predict_trigger_1126(trigger_dict, test_lst):
    """
    trigger predict
    """
    log = trigger_dict['log']
    args = trigger_dict['args']
    labels_map = trigger_dict['labels_map']
    ernie_config = trigger_dict['ernie_config']
    place = trigger_dict['place']
    dev_count = trigger_dict['dev_count']
    reader = trigger_dict['reader']
    startup_prog = trigger_dict['startup_prog']
    test_prog = trigger_dict['test_prog']
    test_pyreader = trigger_dict['test_pyreader']
    graph_vars = trigger_dict['graph_vars']
    nccl2_num_trainers = trigger_dict['nccl2_num_trainers']
    nccl2_trainer_id = trigger_dict['nccl2_trainer_id']
    if 'exe' in trigger_dict:
        exe = trigger_dict['exe']
    else:
        exe = None
    trigger_pred_save_path = args.trigger_pred_save_path
    if os.path.exists(trigger_pred_save_path):
        print('delete old file : %s' % trigger_pred_save_path)
        os.remove(trigger_pred_save_path)
    
    if args.do_test:
        log.error("********************** trigger predict begin **********************")
        test_trigger_lst = predict_wrapper_1126(args, reader, exe, test_prog, test_pyreader,
                                   graph_vars, 1, 'final', test_lst)
        return test_trigger_lst
    else:
        return []
        

def predict_wrapper(args, reader, exe, test_prog, test_pyreader, graph_vars, epoch, steps):
    """predict_wrapper"""

    def label_pred_2_ori(pred_label, ori_2_new_index):
        """label_pred_2_ori"""
        new_label = [u"O"] * len(ori_2_new_index)
        new_index = []

        for k, v in ori_2_new_index.items():
            if v == -1:
                new_index.append(k)
            elif v < len(pred_label):
                new_label[k] = pred_label[v]
        for index in new_index:
            if index == 0 or new_label[index - 1] == u"O" or index == (
                    len(new_label) - 1):
                new_label[index] = u"O"
            else:
                if new_label[index + 1] == u"O":
                    new_label[index] = u"O"
                else:
                    new_label[index] = u"I-{}".format(new_label[index - 1][2:])
        return new_label

    def get_pred_text(tokens, labels):
        """get_pred_text"""
        start, end, event_type = -1, -1, u""
        ret = []
        for i, lb in enumerate(labels):
            if lb == u"O" and start == -1 and end == -1:
                continue
            elif lb == u"O" and start > -1 and end > -1:
                ret.append({
                    "event_type": event_type,
                    "start": start,
                    "end": end,
                    "text": u"".join(tokens[start:end + 1])
                })
                start, end, event_type = -1, -1, u""
            else:
                if start == -1:
                    start, end, event_type = i, i, lb[2:]
                elif lb.startswith(u"B-"):
                    if start > -1 and end > -1:
                        ret.append({
                            "event_type": event_type,
                            "start": start,
                            "end": end,
                            "text": u"".join(tokens[start:end + 1])
                        })
                        start, end, event_type = i, i, lb[2:]
                    else:
                        start, end, event_type = i, i, lb[2:]
                elif lb[2:] == event_type:
                    end = i
                else:
                    ret.append({
                        "event_type": event_type,
                        "start": start,
                        "end": end,
                        "text": u"".join(tokens[start:end + 1])
                    })
                    start, end, event_type = i, i, lb[2:]

        if start >= 0 and end >= 0:
            ret.append({
                "event_type": event_type,
                "start": start,
                "end": end,
                "text": u"".join(tokens[start:end + 1])
            })
        return ret

    batch_size = args.batch_size if args.predict_batch_size is None else args.predict_batch_size
    test_pyreader.decorate_tensor_provider(
        reader.data_generator(
            args.test_set,
            batch_size=batch_size,
            epoch=1,
            dev_count=1,
            shuffle=False))
    res = predict(exe, test_prog, test_pyreader, graph_vars, dev_count=1)
    
    examples = reader.get_examples_by_file(args.test_set)
    tokenizer = reader.tokenizer
    rev_label_map = {v: k for k, v in six.iteritems(reader.label_map)}
    output = []
    print(u"examples {} res {}".format(len(examples), len(res)))
    for example, r in zip(examples, res):
        _id, s = r
        pred_tokens = tokenizer.convert_ids_to_tokens(_id)
        pred_label = [rev_label_map[ss] for ss in s]

        new_label = label_pred_2_ori(pred_label, example.ori_2_new_index)
        pred_ret = get_pred_text(pred_tokens, pred_label)
        pred_2_new_ret = get_pred_text(example.ori_text, new_label)
        output.append(
            json.dumps(
                {
                    "event_id": example.id,
                    "pred_tokens": pred_tokens,
                    "pred_labels": pred_label,
                    "tokens": example.ori_text,
                    "labels": new_label,
                    "pred_trigger_ret": pred_ret,
                    "sentence": example.sentence,
                    "trigger_ret": pred_2_new_ret
                },
                ensure_ascii=False))
    return output


def predict_wrapper_1126(args, reader, exe, test_prog, test_pyreader, graph_vars, epoch, steps, test_lst):
    """predict_wrapper"""
    
    def label_pred_2_ori(pred_label, ori_2_new_index):
        """label_pred_2_ori"""
        new_label = [u"O"] * len(ori_2_new_index)
        new_index = []
        
        for k, v in ori_2_new_index.items():
            if v == -1:
                new_index.append(k)
            elif v < len(pred_label):
                new_label[k] = pred_label[v]
        for index in new_index:
            if index == 0 or new_label[index - 1] == u"O" or index == (
                    len(new_label) - 1):
                new_label[index] = u"O"
            else:
                if new_label[index + 1] == u"O":
                    new_label[index] = u"O"
                else:
                    new_label[index] = u"I-{}".format(new_label[index - 1][2:])
        return new_label
    
    def get_pred_text(tokens, labels):
        """get_pred_text"""
        start, end, event_type = -1, -1, u""
        ret = []
        for i, lb in enumerate(labels):
            if lb == u"O" and start == -1 and end == -1:
                continue
            elif lb == u"O" and start > -1 and end > -1:
                ret.append({
                    "event_type": event_type,
                    "start": start,
                    "end": end,
                    "text": u"".join(tokens[start:end + 1])
                })
                start, end, event_type = -1, -1, u""
            else:
                if start == -1:
                    start, end, event_type = i, i, lb[2:]
                elif lb.startswith(u"B-"):
                    if start > -1 and end > -1:
                        ret.append({
                            "event_type": event_type,
                            "start": start,
                            "end": end,
                            "text": u"".join(tokens[start:end + 1])
                        })
                        start, end, event_type = i, i, lb[2:]
                    else:
                        start, end, event_type = i, i, lb[2:]
                elif lb[2:] == event_type:
                    end = i
                else:
                    ret.append({
                        "event_type": event_type,
                        "start": start,
                        "end": end,
                        "text": u"".join(tokens[start:end + 1])
                    })
                    start, end, event_type = i, i, lb[2:]
        
        if start >= 0 and end >= 0:
            ret.append({
                "event_type": event_type,
                "start": start,
                "end": end,
                "text": u"".join(tokens[start:end + 1])
            })
        return ret
    
    batch_size = args.batch_size if args.predict_batch_size is None else args.predict_batch_size
    test_pyreader.decorate_tensor_provider(
        reader.data_generator_1126(
            test_lst,
            batch_size=batch_size,
            epoch=1,
            dev_count=1,
            shuffle=False))
    res = predict(exe, test_prog, test_pyreader, graph_vars, dev_count=1)
    
    examples = reader._process_examples_by_json(test_lst)
    tokenizer = reader.tokenizer
    rev_label_map = {v: k for k, v in six.iteritems(reader.label_map)}
    output = []
    print(u"examples {} res {}".format(len(examples), len(res)))
    for example, r in zip(examples, res):
        _id, s = r
        pred_tokens = tokenizer.convert_ids_to_tokens(_id)
        pred_label = [rev_label_map[ss] for ss in s]
        
        new_label = label_pred_2_ori(pred_label, example.ori_2_new_index)
        pred_ret = get_pred_text(pred_tokens, pred_label)
        pred_2_new_ret = get_pred_text(example.ori_text, new_label)
        output.append(
                {
                    "event_id": example.id,
                    "pred_tokens": pred_tokens,
                    "pred_labels": pred_label,
                    "tokens": example.ori_text,
                    "labels": new_label,
                    "pred_trigger_ret": pred_ret,
                    "sentence": example.sentence,
                    "trigger_ret": pred_2_new_ret
                })
    return output


if __name__ == '__main__':
    pass
    # prepare_logger(log)
    # print("=========MODEL CONFIG============")
    # print_arguments(args)
    # print("=========MODEL CONFIG============")
    # check_cuda(args.use_cuda)
    # main(args)
