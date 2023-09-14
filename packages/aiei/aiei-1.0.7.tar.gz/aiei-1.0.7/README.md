### Install AIEI

Version is recommended, not required

- python>=3.6
- torch>=1.6.0 (pytorch amp & tensorboard), torchvision

1. install locally: `pip install -v -e .`. With building ops: `AIEI=0 pip install -v -e .`

2. change variable: `base_config.py -> TORCH_MODEL_HOME, config.py -> data_path`


### TODO
- merge multi-scale_pad and get_scale_pad
- add user define path_ckpt
