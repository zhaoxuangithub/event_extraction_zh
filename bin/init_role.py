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

import logging
import multiprocessing
import os

import paddle.fluid as fluid

import reader.task_reader as task_reader
from finetune.sequence_label import create_model
from model.ernie import ErnieConfig
from utils import utils
from utils.args import check_cuda
from utils.args import prepare_logger
from utils.init import init_checkpoint


# def get_role_init_dict(args):
# TODO 2020-11-24
def get_role_init_dict(args, suf):
    """main"""
    # log = logging.getLogger()
    # prepare_logger(log)
    log = logging.getLogger(__name__)
    check_cuda(args.use_cuda)
    labels_map = {}  # label

    for line in utils.read_by_lines(args.label_map_config):
        arr = line.split("\t")
        labels_map[arr[0]] = int(arr[1])
    args.num_labels = len(labels_map)

    print("=========ERNIE CONFIG============")
    ernie_config = ErnieConfig(args.ernie_config_path)
    # ernie_config.print_config()
    print("=========ERNIE CONFIG============")
    if args.use_cuda:
        dev_list = fluid.cuda_places()
        place = dev_list[0]
        print("==============place==================", place)
        # place = dev_list[1]
        dev_count = len(dev_list)
    else:
        place = fluid.CPUPlace()
        dev_count = int(os.environ.get('CPU_NUM', multiprocessing.cpu_count()))
    print("==============place, dev_count==================", place, dev_count)
    reader = task_reader.RoleSequenceLabelReader(
        vocab_path=args.vocab_path,
        labels_map=labels_map,
        max_seq_len=args.max_seq_len,
        do_lower_case=args.do_lower_case,
        in_tokens=args.in_tokens,
        random_seed=args.random_seed,
        task_id=args.task_id)

    if not (args.do_train or args.do_val or args.do_test):
        raise ValueError("For args `do_train`, `do_val` and `do_test`, at "
                         "least one of them must be True.")

    startup_prog = fluid.Program()
    if args.random_seed is not None:
        startup_prog.random_seed = args.random_seed

    if args.do_val or args.do_test:
        test_prog = fluid.Program()
        with fluid.program_guard(test_prog, startup_prog):
            with fluid.unique_name.guard():
                # TODO pyreader_name 再次调整为不同
                test_pyreader, graph_vars = create_model(
                    args,
                    pyreader_name='test_reader_role' + suf,
                    ernie_config=ernie_config)
    
        test_prog = test_prog.clone(for_test=True)

    nccl2_num_trainers = 1
    nccl2_trainer_id = 0

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
    trigger_dict = dict()
    trigger_dict['log'] = log
    trigger_dict['args'] = args
    trigger_dict['labels_map'] = labels_map
    trigger_dict['ernie_config'] = ernie_config
    trigger_dict['place'] = place
    trigger_dict['dev_count'] = dev_count
    trigger_dict['reader'] = reader
    trigger_dict['startup_prog'] = startup_prog
    trigger_dict['test_prog'] = test_prog
    trigger_dict['test_pyreader'] = test_pyreader
    trigger_dict['graph_vars'] = graph_vars
    trigger_dict['nccl2_num_trainers'] = nccl2_num_trainers
    trigger_dict['nccl2_trainer_id'] = nccl2_trainer_id
    trigger_dict['exe'] = exe
    return trigger_dict


def re_use_some(tri_dict, suf):
    ernie_config = tri_dict["ernie_config"]
    startup_prog = tri_dict["startup_prog"]
    args = tri_dict["args"]
    labels_map = tri_dict["labels_map"]
    place = tri_dict["place"]
    reader = task_reader.RoleSequenceLabelReader(
        vocab_path=args.vocab_path,
        labels_map=labels_map,
        max_seq_len=args.max_seq_len,
        do_lower_case=args.do_lower_case,
        in_tokens=args.in_tokens,
        random_seed=args.random_seed,
        task_id=args.task_id)

    startup_prog = fluid.Program()
    if args.random_seed is not None:
        startup_prog.random_seed = args.random_seed

    if args.do_val or args.do_test:
        test_prog = fluid.Program()
        with fluid.program_guard(test_prog, startup_prog):
            with fluid.unique_name.guard():
                # TODO pyreader_name 再次调整为不同
                test_pyreader, graph_vars = create_model(
                    args,
                    pyreader_name='test_reader_role' + suf,
                    ernie_config=ernie_config)
    
        test_prog = test_prog.clone(for_test=True)

    nccl2_num_trainers = 1
    nccl2_trainer_id = 0

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
    return reader, startup_prog, test_prog, test_pyreader, graph_vars, exe


def re_use_exe(tri_dict):
    startup_prog = tri_dict["startup_prog"]
    args = tri_dict["args"]
    place = tri_dict["place"]
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
    return exe


if __name__ == '__main__':
    pass
    # prepare_logger(log)
    # # print_arguments(args)
    # check_cuda(args.use_cuda)
    # main(args)