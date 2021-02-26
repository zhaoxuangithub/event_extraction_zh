#!/bin/bash
set -eux

HERE=$(readlink -f "$(dirname "$0")")
cd ${HERE}/..

export CUDA_VISIBLE_DEVICES=$1
export FLAGS_eager_delete_tensor_gb=0
export FLAGS_fraction_of_gpu_memory_to_use=0.3

DATA_DIR=$2
MODEL_PATH=$3
TRIGGER_CKPT_PATH=$4
ROLE_CKPT_PATH=$5
DICT=$6
# $0表示当前文件位置,$1-$n表示调用当前脚本时,后面传入的参数1-n个

echo -e "-------------------init_trigger_role test --------------------------"
python init_trigger.py --use_cuda true \
                   --do_train false \
                   --do_val false \
                   --do_test true \
                   --batch_size 32 \
                   --init_pretraining_params ${MODEL_PATH}/params \
                   --trigger_pred_save_path ${TRIGGER_CKPT_PATH}/../pred_trigger.json \
                   --chunk_scheme "IOB" \
                   --label_map_config ${DICT}/vocab_trigger_label_map.txt \
                   --train_set ${DATA_DIR}/train.json \
                   --dev_set ${DATA_DIR}/dev.json \
                   --test_set ${DATA_DIR}/test.json \
                   --vocab_path ${MODEL_PATH}/vocab.txt \
                   --ernie_config_path ${MODEL_PATH}/ernie_config.json \
                   --save_steps 500 \
                   --weight_decay  0.01 \
                   --warmup_proportion 0.1 \
                   --validation_steps 100 \
                   --use_fp16 false \
                   --epoch 6 \
                   --max_seq_len 300 \
                   --learning_rate 8e-5 \
                   --skip_steps 20 \
                   --num_iteration_per_drop_scope 1 \
                   --init_checkpoint ${TRIGGER_CKPT_PATH} \
                   --random_seed 1

python init_role.py --use_cuda true \
                   --do_train false \
                   --do_val false \
                   --do_test true \
                   --batch_size 32 \
                   --init_pretraining_params ${MODEL_PATH}/params \
                   --trigger_pred_save_path ${ROLE_CKPT_PATH}/../pred_role.json \
                   --chunk_scheme "IOB" \
                   --label_map_config ${DICT}/vocab_roles_label_map.txt \
                   --train_set ${DATA_DIR}/train.json \
                   --dev_set ${DATA_DIR}/dev.json \
                   --test_set ${DATA_DIR}/test.json \
                   --vocab_path ${MODEL_PATH}/vocab.txt \
                   --ernie_config_path ${MODEL_PATH}/ernie_config.json \
                   --save_steps 500 \
                   --weight_decay  0.0 \
                   --warmup_proportion 0.1 \
                   --validation_steps 100 \
                   --use_fp16 false \
                   --epoch 6 \
                   --max_seq_len 300 \
                   --learning_rate 5e-5 \
                   --skip_steps 20 \
                   --num_iteration_per_drop_scope 1 \
                   --init_checkpoint ${ROLE_CKPT_PATH} \
                   --random_seed 1
