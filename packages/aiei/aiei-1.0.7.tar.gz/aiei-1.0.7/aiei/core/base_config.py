"""
base_config -> config -> cfg_file -> argparse -> conditionally change value
(c) ZL-2020.
@author ZhaoLei
@since 2020.07.25 18:10
"""
import os
import sys
import setproctitle
import json
import argparse
from datetime import datetime
import random
import numpy as np
import torch
import cv2
from ..misc import mix
from ..misc.logger import Logger

assert sys.version_info >= (3, 6, 1), 'python version should be 3.6.1 or newer, because of [F-Strings, namedtuple]'
cfg = None  # absolutely same to cfg in config.py


class SingleInstance(object):
    # it can't be overrided, but Repr can.
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(SingleInstance, cls).__new__(cls)
        return cls._instance


class Args(SingleInstance):
    # args should be added into dic_args in cfg.done() to make effective
    _parse = argparse.ArgumentParser()
    _parse.add_argument('--cfg_file', type=str, default=None, help='config file path')
    _parse.add_argument('--zl', type=int, default=None, choices=[0, 1, 2], help='0 is train, 1 is val, 2 is test')
    _parse.add_argument('--lr', type=float, default=None, help='learning rate')
    _parse.add_argument('--epochs', type=int, default=None, help='epochs')
    _parse.add_argument('--batch_size', type=int, default=None, help='batch size per gpu')
    _parse.add_argument('--log_path', type=str, default=None, help='log_path')
    _parse.add_argument('--gpus', type=str, default='d0,1,2,3', help='CUDA_VISIBLE_DEVICES(e.g.: d0,1,2) or NUM_GPUS(e.g.: 8)')
    _parse.add_argument('--port', type=str, default='10080', help='Distribute Port')
    _parse.add_argument('--model_home', type=str, default=None, help='model_home')
    _parse.add_argument('--local_rank', type=int, default=0, help='local_rank')
    _parse.add_argument('--opencv_num_threads', type=int, default=0, help='opencv_num_threads: avoid cpu overload')
    _parse.add_argument('--note', type=str, default='"Ephemeris 339, log number 24"', help='experiment note')

    @classmethod
    def add(cls, *args, **kwargs):
        cls._parse.add_argument(*args, **kwargs)
        return cls

    @classmethod
    def update(cls):
        dic_namespace = cls._parse.parse_args().__dict__
        for key, value in dic_namespace.items():
            setattr(cls, key, value)


class Repr():
    Args.update()  # the params with Args is required (can't be None)
    # class property -> __new__ -> __init__(new object) -> self
    _CLS_CHILD = {}  # dict: avoid overriding by multiple children, key is the class name of child

    @classmethod
    def _pretty_dict(cls, zdic, zindent=2):
        def pretty(dic, indent):
            INNER_INDENT = 2
            res = ''
            for key, value in dic.items():
                res += f'{" " * INNER_INDENT * indent}\'{key}\': '
                if isinstance(value, dict):
                    res += f'{{\n{pretty(value, indent + 1)}{" " * INNER_INDENT * indent}}},\n'
                else:
                    if isinstance(value, str):
                        value = f'\'{value}\''
                    res += f'{value},\n'
            return res

        return f'{{\n{pretty(zdic, zindent)[:-1]}\n  }}'  # -1: remove last '\n'

    @classmethod
    def _walk(cls, zcls):  # zcls to dict, cls is REPR(parent)
        dic = {}
        for key, value in zcls.__dict__.items():  # zcls.__dict__ == vars(zcls)
            if key.startswith('__') or key == '_instance':
                continue
            if '<class' in str(value):
                value = Repr._walk(value)
            dic[key] = value
        return dic

    def __new__(cls, *args, **kwargs):
        str_cls = str(cls)
        Repr._CLS_CHILD[str_cls] = cls  # cls == zcls(child)
        # cls._instance = {} make Repr be single instance and overrided
        if not hasattr(cls, '_instance'):
            cls._instance = {}
        if str_cls not in cls._instance.keys():
            cls._instance[str_cls] = super().__new__(cls)
        # merge cls_parent's attributes into cls_child (in order to repr cls_parent's attributes)
        for name, item in cls._instance.items():
            cls_parent = type(item)
            if cls != cls_parent and issubclass(cls, cls_parent):
                for key, value in cls_parent.__dict__.items():
                    if key.startswith('__') or key == '_instance' or key in cls.__dict__:
                        continue
                    setattr(cls, key, value)
        return cls._instance[str_cls]

    def __repr__(self):
        # str_res = json.dumps(Repr.RES_DIC, indent=2)  # NOT UNIFORM(e.g.: None to null, False to false, '' to "")
        str_cls = str(type(self))  # type(self) == self.__class__
        # placed here(NOT __new__) for showing update attributes correctly
        dic_default = Repr._walk(Repr._CLS_CHILD[str_cls])  # default attributes
        dic_update = Repr._walk(self)  # after self update attributes
        dic_default.update(dic_update)  # merge
        return f'<zrepr_cls>{Repr._pretty_dict(dic_default)}'


class FEAT(Repr):
    AMP = False
    SYNC_BN = False
    PROFILE = False

    class WARM_UP_LR():
        STEP = -1  # -1 means not use warm up lr

    class GRAD_CLIP():
        MAX_NORM = None  # None means not use grad_clip
        NORM_TYPE = 2
        CLIP_VALUE = None

    class GROUP_SAMPLER():
        TRAIN = False
        EVAL = False


class TRAIN(Repr):
    BATCH_SIZE = Args.batch_size  # same to imgs_per_gpu
    EPOCHS = Args.epochs
    LR = Args.lr
    LR_SCHEDULER = None
    RESUME = True
    EVAL_FREQ = 1  # per n epoch eval model. 0: no EVAL during TRAIN


class EVAL(Repr):
    BATCH_SIZE = None  # EVAL_BATCH_SIZE
    USE_BEST_CKPT = False


class LOG(Repr):
    INS: Logger = None
    PATH = Args.log_path
    PATH_ZID = None
    FREQ = 100


class AIEI(Repr):
    # FEAT = FEAT  # Not FEAT = FEAT()
    TORCH_MODEL_HOME = None
    EXP_ZID = 'main'  # key in zlogs.json
    LOCAL_RANK = Args.local_rank
    # python -m torch.distributed.launch --nproc_per_node 4 main.py --zl 0
    DISTRIBUTED = 'local_rank' in ''.join(sys.argv)
    WORLD_SIZE = 1
    SEED = None
    GPUS = 'd0,1,2,3'  # see Args.gpus
    NUM_DATA_WORKERS = len(GPUS.split(',')) + 1
    FIND_UNUSED_PARAMETERS = False


class BaseConfig(SingleInstance):
    def __init__(self):
        super().__init__()
        self.ZL = Args.zl  # 0: train, 1: val, 2: test
        self.AIEI = AIEI()
        self.TRAIN = TRAIN()
        self.EVAL = EVAL()
        self.LOG = LOG()
        self.FEAT = FEAT()
        # self._OPTIONS = ['IN_SHAPE', 'EVAL_BATCH_SIZE', 'LR_SCHEDULER', 'SEED']

    def _update_params(self):
        # update params from cfg_file
        if Args.cfg_file is not None:
            file_name = Args.cfg_file.split('/')[-1].split('.')[0]
            exec(f'from cfg import {file_name} as zcfg')
            eval('zcfg.update(self)')
        # update params from argparse
        dic_args = {
            'ZL': 'zl', 'TRAIN.LR': 'lr', 'TRAIN.EPOCHS': 'epochs', 'TRAIN.BATCH_SIZE': 'batch_size', 'LOG.PATH': 'log_path',
            'AIEI.GPUS': 'gpus'
        }
        for item, value in dic_args.items():
            exec(f'self.{item} = self.{item} if Args.{value} is None else Args.{value}')

    def _init_log(self):
        zl = {}
        if not os.path.exists(self.LOG.PATH) and self.AIEI.LOCAL_RANK == 0:
            os.makedirs(self.LOG.PATH)
        if os.path.exists(f'{self.LOG.PATH}/zlogs.json'):
            with open(f'{self.LOG.PATH}/zlogs.json') as fp:
                try:
                    zl = json.load(fp)
                except Exception as e:
                    Logger.zprint('torch.distributed.launch did not exit completely, please kill the process and restart' + e.msg,
                        self.AIEI.LOCAL_RANK, Logger.COLOR.RED)
                if f'zid_{self.AIEI.EXP_ZID}' not in zl.keys():
                    zl[f'zid_{self.AIEI.EXP_ZID}'] = ''
                fp.close()
        else:
            zl[f'zid_{self.AIEI.EXP_ZID}'] = ''
        if not self.TRAIN.RESUME or zl[f'zid_{self.AIEI.EXP_ZID}'] == '':
            zl[f'zid_{self.AIEI.EXP_ZID}'] = datetime.now().strftime('z%y%m%d%H%M') if self.AIEI.EXP_ZID != 'debug' else 'debug'
        # if 'debug' in self.EXP_ZID:
        if 'main.py' not in sys.argv[0]:  # debug !main.py file.
            self.LOG.PATH_ZID = f'{self.LOG.PATH}/debug'
        else:
            if self.AIEI.LOCAL_RANK == 0:
                with open(f'{self.LOG.PATH}/zlogs.json', 'w') as fp:
                    json.dump(zl, fp, indent=4)
                    fp.close()
            self.LOG.PATH_ZID = f'{self.LOG.PATH}/{zl[f"zid_{self.AIEI.EXP_ZID}"]}'
        if self.LOG.INS is None:
            self.LOG.INS = Logger(self.LOG.PATH_ZID, self.AIEI.LOCAL_RANK, log_name='train.log' if self.ZL == 0 else 'eval.log')

        # msgs
        Logger.zprint(f'*****You are using zid_{self.AIEI.EXP_ZID} {self.LOG.PATH_ZID.split("/").pop()}*****',
            self.AIEI.LOCAL_RANK, Logger.COLOR.BG_WHITE + Logger.COLOR.BLACK)
        if 'CUDA_LAUNCH_BLOCKING' in os.environ and os.environ['CUDA_LAUNCH_BLOCKING'] == '1':
            self.LOG.INS.warning('CUDA_LAUNCH_BLOCKING is opening, which will slow down the training speed considerably!', False)

        # seed for reproducibility
        if self.AIEI.SEED is not None:
            seed = self.AIEI.SEED + self.AIEI.LOCAL_RANK
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            self.LOG.INS.warning(
                'You have chosen to seed training. This will turn on the CUDNN deterministic setting, '
                'which can slow down your training considerably!', False)

    def _check_params(self):
        for key, value in vars(self).items():
            if key not in self._OPTIONS:
                assert value is not None, f'{key} is None'

    def _set_environ(self):
        cv2.setNumThreads(Args.opencv_num_threads)  # avoid cpu overload
        os.environ['MASTER_ADDR'] = '127.0.0.1'
        # bugs: Causes startup to freeze because of getting different ports
        # os.environ['MASTER_PORT'] = f'{_try_port(10080)}'
        os.environ['MASTER_PORT'] = Args.port
        os.environ['OMP_NUM_THREADS'] = '1'
        # os.environ['MKL_NUM_THREADS'] = '1'
        if self.AIEI.TORCH_MODEL_HOME is not None:
            os.environ['TORCH_HOME'] = self.AIEI.TORCH_MODEL_HOME
        # os.environ['CUDA_LAUNCH_BLOCKING'] = '1'  # debug 'device-side assert triggered' error
        if 'd' == self.AIEI.GPUS[0]:
            os.environ['CUDA_VISIBLE_DEVICES'] = self.AIEI.GPUS[1:]
            self.AIEI.GPUS = len(self.AIEI.GPUS[1:].split(','))
        else:
            self.AIEI.GPUS = int(self.AIEI.GPUS)
            os.environ['CUDA_VISIBLE_DEVICES'] = ','.join([str(i) for i in range(self.AIEI.GPUS)])

    def _debug_mode(self):
        # IDE debug or not using distributed mode
        if sys.argv[0][0] == '/' or not self.AIEI.DISTRIBUTED:
            Logger.zprint('*****DEBUG OR NOT DISTRIBUTED MODE*****', style=Logger.COLOR.REVERSE)
            # os.environ['CUDA_VISIBLE_DEVICES'] = '3'
            self.AIEI.GPUS = 1
            self.AIEI.NUM_DATA_WORKERS = 0  # 0: w/o using multiprocess (capture.read() will be stuck if > 0)
            self.AIEI.DISTRIBUTED = False
            self.FEAT.AMP = False
            self.FEAT.SYNC_BN = False
            if sys.argv[0][0] == '/':
                self.AIEI.EXP_ZID = 'debug'

    def done(self):
        global cfg
        self._update_params()
        self._set_environ()
        self._init_log()
        # self._check_params()
        self._debug_mode()
        setproctitle.setproctitle(f'python {self.AIEI.EXP_ZID}.py')
        self._RECORD = {'HOST_INFO': mix.get_host_info(), 'NOTE': Args.note, 'CFG_FILE': Args.cfg_file}
        cfg = self  # type: BaseConfig


class ABC(BaseConfig):
    def __init__(self):
        super(ABC, self).__init__()
        self.input_shape = (12, 12)
        self.lr = 0.001
        self.FEAT.WARM_UP_LR.STEP = 90000


if __name__ == '__main__':
    # if SingleInstance, ABC can't change parent value after ctreating BaseConfig.
    # So BaseConfig NOT be created firstly, or extend object
    t_cfg = ABC()
    # three = ABC()
    print(t_cfg)
    # print(id(t_cfg) == id(three))

    import pprint
    print(pprint.pformat(vars(t_cfg), indent=2, depth=50))  # show attributes
