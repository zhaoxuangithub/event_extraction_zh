#!/bin/bash
set -eux

echo -e "export some path"
export CUDA_VISIBLE_DEVICES=0
export FLAGS_eager_delete_tensor_gb=0
export FLAGS_fraction_of_gpu_memory_to_use=0.3
