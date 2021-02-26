import os
from finetune_args import parser


def get_common_args(pa):
	"""
	根据pa路径获取 通用的args
	"""
	args = parser.parse_args()
	# /home/zx/DuEE_baseline pa路径
	args.use_cuda = True
	args.do_train = False
	args.do_val = False
	args.do_test = True
	args.batch_size = 32
	args.init_pretraining_params = os.path.join(pa, "model/ERNIE_1.0_max-len-512/params")
	args.trigger_pred_save_path = os.path.join(pa, "save_model/trigger/pred_trigger.json")
	args.chunk_scheme = "IOB"
	args.label_map_config = os.path.join(pa, "dict/vocab_trigger_label_map.txt")
	args.train_set = os.path.join(pa, "data/train.json")
	args.dev_set = os.path.join(pa, "data/dev.json")
	args.test_set = os.path.join(pa, "data/test.json")
	args.vocab_path = os.path.join(pa, "model/ERNIE_1.0_max-len-512/vocab.txt")
	args.ernie_config_path = os.path.join(pa, "model/ERNIE_1.0_max-len-512/ernie_config.json")
	args.save_steps = 500
	args.weight_decay = 0.01
	args.warmup_proportion = 0.1
	args.validation_steps = 100
	args.use_fp16 = False
	args.epoch = 6
	args.max_seq_len = 300
	args.learning_rate = 8e-5
	args.skip_steps = 20
	args.num_iteration_per_drop_scope = 1
	args.init_checkpoint = os.path.join(pa, "save_model/trigger/final_model")
	args.random_seed = 1
	return args


def format2_role_args(arg, pa):
	arg.trigger_pred_save_path = os.path.join(pa, "save_model/role/pred_role.json")
	arg.label_map_config = os.path.join(pa, "dict/vocab_roles_label_map.txt")
	arg.weight_decay = 0.0
	arg.init_checkpoint = os.path.join(pa, "save_model/role/final_model")
	return arg


def get_role_args(pa):
	"""
	根据pa路径获取 role的args
	"""
	print("+++++++++++++++++get role args+++++++++++++++++++++")
	args = parser.parse_args()
	# /home/zx/DuEE_baseline pa路径
	args.use_cuda = True
	args.do_train = False
	args.do_val = False
	args.do_test = True
	args.batch_size = 32
	args.init_pretraining_params = os.path.join(pa, "model/ERNIE_1.0_max-len-512/params")
	args.trigger_pred_save_path = os.path.join(pa, "save_model/role/pred_role.json")
	args.chunk_scheme = "IOB"
	args.label_map_config = os.path.join(pa, "dict/vocab_roles_label_map.txt")
	args.train_set = os.path.join(pa, "data/train.json")
	args.dev_set = os.path.join(pa, "data/dev.json")
	args.test_set = os.path.join(pa, "data/test.json")
	args.vocab_path = os.path.join(pa, "model/ERNIE_1.0_max-len-512/vocab.txt")
	args.ernie_config_path = os.path.join(pa, "model/ERNIE_1.0_max-len-512/ernie_config.json")
	args.save_steps = 500
	args.weight_decay = 0.0
	args.warmup_proportion = 0.1
	args.validation_steps = 100
	args.use_fp16 = False
	args.epoch = 6
	args.max_seq_len = 300
	args.learning_rate = 8e-5
	args.skip_steps = 20
	args.num_iteration_per_drop_scope = 1
	args.init_checkpoint = os.path.join(pa, "save_model/role/final_model")
	args.random_seed = 1
	return args
