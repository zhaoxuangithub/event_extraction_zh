#!/bin/bash

:<<!
针对test.json进行预测
!

HERE=$(readlink -f "$(dirname "$0")")
echo ${HERE}/..
cd ${HERE}/..

DATA_DIR=${HERE}/../../data
PRETRAIN_MODEL=${HERE}/../../model/ERNIE_1.0_max-len-512
SAVE_MODEL=${HERE}/../../save_model
DICT=${HERE}/../../dict
GPUID=0

#RESULT_DIR=${HERE}/../../result


# 目录不存在先创建
if [ ! -d ${SAVE_MODEL} ]; then
    mkdir ${SAVE_MODEL}
fi

TRIGGER_SAVE_MODEL=${SAVE_MODEL}/trigger
ROLE_SAVE_MODEL=${SAVE_MODEL}/role


# 初始化trigger/role以及加载模型
echo -e "\n\n**********INIT TRIGGER ROLE START**********"
sh script/init_trigger_role.sh ${GPUID} ${DATA_DIR} ${PRETRAIN_MODEL} ${TRIGGER_SAVE_MODEL}/final_model ${ROLE_SAVE_MODEL}/final_model ${DICT}
echo "**********INIT TRIGGER ROLE END**********"
