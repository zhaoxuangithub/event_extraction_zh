#!/bin/bash

:<<!
训练模型并评估 步骤4
!

HERE=$(readlink -f "$(dirname "$0")")
echo ${HERE}
cd ${HERE}/..

DATA_DIR=${HERE}/../../data
PRETRAIN_MODEL=${HERE}/../../model/ERNIE_1.0_max-len-512
SAVE_MODEL=${HERE}/../../save_model
DICT=${HERE}/../../dict
GPUID=0

RESULT_DIR=${HERE}/../../result


# 目录不存在先创建
if [[ ! -d ${SAVE_MODEL} ]]; then
    mkdir ${SAVE_MODEL}
fi

TRIGGER_SAVE_MODEL=${SAVE_MODEL}/trigger
ROLE_SAVE_MODEL=${SAVE_MODEL}/role

# STEP 1: 训练触发词模型
echo -e "**********TRIGGER TRAIN START**********"
if [[ -d ${TRIGGER_SAVE_MODEL}/final_model ]]; then
    echo "trigger model is trained"
else
    echo "sh script train_event_trigger.sh shfile start..."
    sh script/train_event_trigger.sh ${GPUID} ${DATA_DIR} ${TRIGGER_SAVE_MODEL} ${PRETRAIN_MODEL} ${DICT}
fi
echo "**********TRIGGER TRAIN END**********"


# STEP 2: 预测句子触发词识别的结果
echo -e "\n\n**********TRIGGER PREDICT START**********"

