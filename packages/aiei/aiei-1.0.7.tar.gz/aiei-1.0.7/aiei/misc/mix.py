"""
(c) ZL-2020.
@author ZhaoLei
@since 2020.06.24 11:52
"""
import os
import sys
import shutil
import json
import torch
import numpy as np
import cv2
import subprocess
import re
from datetime import datetime
import traceback
import platform
import socket
import time
import cProfile
import collections
from functools import partial
from torchvision.models import utils as tv_utils
import itertools
from tabulate import tabulate


class AverageMeter(object):
    def __init__(self, ignore=0):
        self.reset()
        self.value = 0
        self.avg = 0
        self.sum = 0
        self.count = 0
        self.ignore = ignore
        self.ignore_count = 0

    def reset(self):
        self.value = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, value, num=1):
        if self.ignore_count < self.ignore:
            self.ignore_count += num
            return
        self.value = value
        self.sum += value * num
        self.count += num
        self.avg = self.sum / self.count


def save_checkpoint(state, is_best, ckpt_dir, info):
    if not os.path.exists(ckpt_dir):
        os.mkdir(ckpt_dir)
    torch.save(state, f'{ckpt_dir}/ckpt.pth.tar')
    if is_best:
        shutil.copyfile(f'{ckpt_dir}/ckpt.pth.tar', f'{ckpt_dir}/best.pth.tar')
    with open(f'{ckpt_dir}/info.json', 'w') as fp:
        json.dump(info, fp, indent=4)


def save_model(state, checkpoint_dir='logs/ckpt'):
    if not os.path.exists(checkpoint_dir):
        os.mkdir(checkpoint_dir)
    filename = 'checkpoint_{}.pth.tar'.format(state['epoch'])
    file_path = os.path.join(checkpoint_dir, filename)
    torch.save(state, file_path)


def generate_heat_map(heat_map, pts, sigma):
    heat_map[int(pts[1])][int(pts[0])] = 1
    heat_map = cv2.GaussianBlur(heat_map, sigma, 0)
    am = np.amax(heat_map)
    heat_map /= (am / 255)
    return heat_map


def get_gpu_info():
    # dev = subprocess.check_output("nvidia-smi | grep MiB | awk -F '|' '{print $3}' | awk -F '/' '{print $1}' |
    #  grep -Eo '[0-9]{1,10}'", shell=True).decode()
    dev = subprocess.check_output("nvidia-smi | grep MiB | awk -F '|' '{print $3$4}' ", shell=True).decode()
    dev = [re.sub('[ /a-ln-zA-LN-Z]+', ' ', zl)[1:-1].split(' ') for zl in dev.split('\n') if zl != '']
    dev = [f'{zl[0]}-{zl[-1]}' for zl in dev]
    return dev


def get_host_info():
    info = {}
    uname = platform.uname()
    info['SYSTEM'] = uname.system
    info['NODE'] = uname.node
    info['PROCESSOR'] = uname.processor
    info['RELEASE'] = uname.release
    return info


def dict_to_md_table(dic):
    str_md = """
| key | value |
| --- | --- |
"""
    for key, value in dic.items():  # can also import tabulate.tabulate
        str_md += f'| {key} | {value} |\n'
    return str_md


def bak_src_zip(logs_path_zid, rm=True):
    def ignore_copy_files(path, content):
        to_ignore = []
        # print('eeeeeeeee', path, content)
        for file_name in content:
            if file_name in ['doc', 'zlogs', '__pycache__']:  # ignore dir
                to_ignore.append(file_name)
            elif os.path.isfile(f'{path}/{file_name}'):  # ignore files
                if re.search('.so|.jpg|.mp4|.tar|.pth', file_name) is not None:
                    to_ignore.append(file_name)
        return to_ignore

    path_zlibs = f'{os.path.dirname(__file__)}/../'
    path_proj = f'{logs_path_zid}/../../'
    try:
        if os.path.exists(f'{logs_path_zid}/zsrc'):
            shutil.rmtree(f'{logs_path_zid}/zsrc')
        shutil.copytree(path_zlibs, f'{logs_path_zid}/zsrc/zlibs', ignore=ignore_copy_files)
        shutil.copytree(path_proj, f'{logs_path_zid}/zsrc/user', ignore=ignore_copy_files)
        subprocess.check_output(f"cd {logs_path_zid}; tar -zcvf zsrc_{datetime.now().strftime('%y%m%d_%H%M')}.tar.gz zsrc; "
            f"{'rm -rf zsrc' if rm else ''}", shell=True)  # ignore output (not show)
    except Exception as e:
        traceback.print_exc()


def copy_file(src, dst, locak_rank):
    if locak_rank > 0:
        return
    shutil.copy(src, dst)


def get_exc_info(is_trace=True):
    if is_trace:
        format_info = traceback.format_exc()
    else:
        exec_info = sys.exc_info()
        tb_frame = exec_info[2].tb_frame
        format_info = f'***File {tb_frame.f_code.co_filename}, function {tb_frame.f_code.co_name}, ' \
                      f'line {exec_info[2].tb_lineno}, {exec_info[2].tb_lasti}, {exec_info[1]}***\n'
    return format_info


def find_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))  # Binding to port 0 will cause the OS to find an available port
    port = sock.getsockname()[1]
    sock.close()
    print(f'use free port {port}')
    return port


def try_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        for _ in range(0, 10):
            try:
                sock.bind(('127.0.0.1', port))
                break
            except IOError as e:
                print(f'port {port} is in use, try port {port + 1}')
                port += 1
        sock.close()
    return port


def get_torch_version():
    return tuple([int(x) for x in torch.__version__.split('.')[:2]])


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (time2 - time1) * 1000.0))
        return ret

    return wrap


def profile(name, logs_path_zid='./'):
    def fn_profile(fn):
        def wrap(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            ret = fn(*args, **kwargs)
            pr.disable()
            pr.dump_stats(f'{logs_path_zid}/{name}.prof')
            os.system(f'cd {logs_path_zid}; flameprof {name}.prof > {name}.svg; rm {name}.prof')
            print(f'{name}.svg have saved in {logs_path_zid}. Use browser to visualize it.')
            return ret

        return wrap

    return fn_profile


def get_num_params(model):
    return round(sum(p.numel() for p in model.parameters()) / (1024 * 1024), 2)


def load_state_dict_from_url(model, url, model_dir, msg=''):
    # rewrite to control model_dir and map_location
    state_dict = model.state_dict()
    pre_state_dict = tv_utils.load_state_dict_from_url(url, model_dir=model_dir, map_location=lambda storage, loc: storage)
    count = 0
    for k, v in pre_state_dict.items():
        if k not in state_dict:
            continue
        state_dict[k] = v
        count += 1
    print(f'Successfully load {count} keys(Expected: {len(state_dict.keys())}, Origin: {len(pre_state_dict.keys())}). {msg}')
    model.load_state_dict(state_dict)
    # for param in self.parameters():
    #     param.requires_grad = False
    return model


def tree_dict():
    tree = lambda: collections.defaultdict(tree)
    dic = tree()
    # dic['s1']['s2']['s3'] = 'abc'
    # print(json.dumps(dic))  # {"s1": {"s2": {"s3": "yello"}}}
    return dic


def multi_apply(func, *args, **kwargs):
    pfunc = partial(func, **kwargs) if kwargs else func
    map_results = map(pfunc, *args)
    return tuple(map(list, zip(*map_results)))


# with depth os.walk
def lwalk(target_dir, max_depth=10000):
    if max_depth == 0:
        return
    dirs, nondirs = [], []
    with os.scandir(target_dir) as it:
        for entry in it:
            if entry.is_dir():
                dirs.append(entry.name)
            else:
                nondirs.append(entry.name)
        yield target_dir, dirs, nondirs
        for dirname in dirs:
            new_path = os.path.join(target_dir, dirname)
            yield from lwalk(new_path, max_depth - 1)


if __name__ == '__main__':
    print(get_gpu_info())
