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

RESULT_DIR=${HERE}/../../result


# 目录不存在先创建
if [ ! -d ${SAVE_MODEL} ]; then
    mkdir ${SAVE_MODEL}
fi

TRIGGER_SAVE_MODEL=${SAVE_MODEL}/trigger
ROLE_SAVE_MODEL=${SAVE_MODEL}/role


# 预先删除gold.json 和 pred.json文件
echo -e "\n\n**********delete gold.json and pred.json file**********"
# 先判断gold.json 文件是否存在, 存在则删除
if [ -e ${RESULT_DIR}/gold.json ] ;then
  echo "gold.json is exists rm it"
  rm -f ${RESULT_DIR}/gold.json
else
  echo "gold.json is not exists"
fi

# 先判断pred.json 文件是否存在, 存在则删除
if [ -e ${RESULT_DIR}/pred.json ] ;then
  echo "pred.json is exists rm it"
  rm -f ${RESULT_DIR}/pred.json
else
  echo "pred.json is not exists"
fi


# STEP 5: 预测结果处理成评估需要的格式
echo -e "\n\n**********RESULT START**********"
python predict_eval_process.py test_data_2_eval ${DATA_DIR}/test.json ${RESULT_DIR}/gold.json # 测试集转化为评估格式
TRIGGER_PRED_FILE=${TRIGGER_SAVE_MODEL}/pred_trigger.json
ROLE_PRED_FILE=${ROLE_SAVE_MODEL}/pred_role.json
if [ ! -e ${TRIGGER_PRED_FILE} ] || [ ! -e ${ROLE_PRED_FILE} ]; then
    echo "check trigger or role extract is finished"
else
    python predict_eval_process.py predict_data_2_eval ${TRIGGER_PRED_FILE} ${ROLE_PRED_FILE} ${DICT}/event_schema.json ${RESULT_DIR}/pred.json
fi

echo "**********RESULT END**********"
