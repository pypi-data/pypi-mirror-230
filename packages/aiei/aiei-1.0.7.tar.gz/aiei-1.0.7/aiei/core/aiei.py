"""
(c) ZL-2020.
@author ZhaoLei
@since 2020.06.24 11:03
"""
import os
import sys
import pprint
import time
import socket
import shutil
from datetime import datetime
from tqdm import tqdm
import cProfile
import torch
from torch import nn
from torch.backends import cudnn
from torch import distributed as dist
from torch.cuda import amp
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torch.utils.tensorboard import SummaryWriter

from .base_config import cfg
from ..data.sampler import GroupSampler, DistributedGroupSampler
from ..misc import mix, summary
from ..misc.logger import Logger
from ..model import function


def _init_params():
    try:
        cfg._RECORD  # create in cfg.done()
    except Exception as e:
        raise ValueError(f'{e}. You should add "cfg.done()" afetr "cfg = Config()" or import core.aiei shouled be after config')
    # torch.cuda.init()
    cudnn.benchmark = True
    cudnn.deterministic = False if cfg.AIEI.SEED is None else True
    cudnn.enabled = True
    zl_state = 'local_rank' in ''.join(sys.argv)
    assert not (zl_state != cfg.AIEI.DISTRIBUTED), f'Check your command or set cfg.AIEI.DISTRIBUTED to {zl_state}'
    path_writer = f'{cfg.LOG.PATH_ZID}/run/{datetime.now().strftime("%d%H%M")}'
    if sys.argv[0][0] == '/':  # debug
        path_writer = f'{cfg.LOG.PATH}/debug/run'
        if os.path.exists(path_writer):
            shutil.rmtree(path_writer)
    writer = None
    if cfg.AIEI.LOCAL_RANK == 0 and cfg.ZL == 0:
        writer = SummaryWriter(path_writer)
    if cfg.AIEI.DISTRIBUTED:
        # cfg.local_rank == dist.get_rank(), .cuda() == .cuda(cfg.local_rank)
        torch.cuda.set_device(cfg.AIEI.LOCAL_RANK % cfg.AIEI.GPUS)
        dist.init_process_group(backend='nccl', init_method='env://')
        cfg.AIEI.WORLD_SIZE = dist.get_world_size()
        dist.barrier()
        # cfg.lr = cfg.lr * float(cfg.batch_size * cfg.world_size)
    if cfg.ZL == 0:  # record cfg. if no indent, should change width=1
        cfg.LOG.INS.info(f'\n{pprint.pformat(vars(cfg), indent=2, depth=4)}')
    return writer


def _init_model(model, optimizer=None):
    cfg.LOG.INS.info(f'Total Params: {mix.get_num_params(model)}MB, World Size: {cfg.AIEI.WORLD_SIZE}, AMP: {cfg.FEAT.AMP}')
    model = model.cuda()
    if cfg.FEAT.SYNC_BN:
        if cfg.AIEI.LOCAL_RANK == 0:
            print('using synced BN')
        model = function.convert_syncbn_model(model)
    if cfg.AIEI.DISTRIBUTED:
        model = nn.parallel.DistributedDataParallel(model, device_ids=[cfg.AIEI.LOCAL_RANK],
            find_unused_parameters=cfg.AIEI.FIND_UNUSED_PARAMETERS)
    else:
        model = nn.DataParallel(model, device_ids=list(range(cfg.AIEI.GPUS)))  # easy memory unbalance with big model
    return model, optimizer


def _init_train_loader(train_dataset, collate_fn=None):
    if train_dataset is None:
        return None, None
    if collate_fn is None and mix.get_torch_version() <= (1, 1):
        collate_fn = torch.utils.data.dataloader.default_collate
    if cfg.AIEI.DISTRIBUTED:
        train_sampler = DistributedGroupSampler(train_dataset,
            samples_per_gpu=cfg.TRAIN.BATCH_SIZE) if cfg.FEAT.GROUP_SAMPLER.TRAIN else DistributedSampler(train_dataset)
    else:
        train_sampler = GroupSampler(train_dataset,
            samples_per_gpu=cfg.TRAIN.BATCH_SIZE) if cfg.FEAT.GROUP_SAMPLER.TRAIN else None
        cfg.TRAIN.BATCH_SIZE = cfg.TRAIN.BATCH_SIZE * cfg.AIEI.GPUS
    train_loader = DataLoader(train_dataset, batch_size=cfg.TRAIN.BATCH_SIZE, shuffle=(train_sampler is None),
        num_workers=cfg.AIEI.NUM_DATA_WORKERS, pin_memory=True, sampler=train_sampler, collate_fn=collate_fn, drop_last=True)
    return train_loader


def _init_eval_loader(eval_dataset, collate_fn=None):
    if eval_dataset is None:
        return None
    batch_size = cfg.TRAIN.BATCH_SIZE
    if cfg.EVAL.BATCH_SIZE is not None:
        batch_size = cfg.EVAL.BATCH_SIZE
    if collate_fn is None and mix.get_torch_version() <= (1, 1):
        collate_fn = torch.utils.data.dataloader.default_collate
    if cfg.AIEI.DISTRIBUTED:
        eval_sampler = DistributedGroupSampler(eval_dataset,
            samples_per_gpu=batch_size) if cfg.FEAT.GROUP_SAMPLER.EVAL else DistributedSampler(eval_dataset)
    else:
        eval_sampler = GroupSampler(eval_dataset, samples_per_gpu=batch_size) if cfg.FEAT.GROUP_SAMPLER.EVAL else None
        batch_size = batch_size * cfg.AIEI.GPUS
    eval_loader = DataLoader(eval_dataset, batch_size=batch_size, shuffle=False, num_workers=cfg.AIEI.NUM_DATA_WORKERS,
        pin_memory=True, sampler=eval_sampler, collate_fn=collate_fn, drop_last=False)
    return eval_loader


def _feat_grad_clip(model_params):
    # use clip_grad, speed up: call model.parameters() before iteration
    if cfg.FEAT.GRAD_CLIP.MAX_NORM is not None:
        nn.utils.clip_grad_norm_(model_params, max_norm=cfg.FEAT.GRAD_CLIP.MAX_NORM, norm_type=cfg.FEAT.GRAD_CLIP.NORM_TYPE)
    if cfg.FEAT.GRAD_CLIP.CLIP_VALUE is not None:
        nn.utils.clip_grad_value_(model_params, clip_value=cfg.FEAT.GRAD_CLIP.CLIP_VALUE)


class Runner(object):
    def __init__(self, model=None, optimizer=None, criterion=None, train_dataset=None, eval_dataset=None, **kwargs):
        support_kwargs = ['train_collate_fn', 'eval_collate_fn']
        for key in kwargs:
            assert key in support_kwargs, Logger.zstr(f'Not support {key}, arg should be one of {support_kwargs}',
                Logger.COLOR.ASSERT)
        assert model is not None, Logger.zstr('Model is None', Logger.COLOR.ASSERT)
        self.global_step = 0
        self._start_epoch = 0
        self._best_epoch = 0
        self._best_accuracy = 0.0
        self.writer = _init_params()  # type: SummaryWriter
        self.model, self.optimizer = _init_model(model, optimizer)
        self.criterion = None if criterion is None else criterion.cuda()
        self._scaler = amp.GradScaler(enabled=cfg.FEAT.AMP)
        if cfg.TRAIN.RESUME:
            self._resume()  # before scheduler
        self._lr_scheduler = None if optimizer is None else self.et_scheduler(-1 if self._start_epoch == 0 else self._start_epoch)
        self._train_loader = _init_train_loader(
            train_dataset, kwargs['train_collate_fn'] if
            ('train_collate_fn' in kwargs and kwargs['train_collate_fn'] is not None) else None)
        self._eval_loader = _init_eval_loader(
            eval_dataset, kwargs['eval_collate_fn'] if
            ('eval_collate_fn' in kwargs and kwargs['eval_collate_fn'] is not None) else None)

    def _resume(self):
        # TODO For compatibility, key('extras'/'steps'/'perf_AP') is old version
        path_ckpt_file = f'{cfg.LOG.PATH_ZID}/ckpt/ckpt.pth.tar'
        # path_ckpt_file = 'det/centernet/zlogs/resdcn18/res18dcn.pth'
        path_best_ckpt_file = f'{cfg.LOG.PATH_ZID}/ckpt/best.pth.tar'
        if cfg.ZL != 0 and cfg.EVAL.USE_BEST_CKPT:
            path_ckpt_file = path_best_ckpt_file
        if os.path.exists(path_ckpt_file):
            # NOTE: map_location equal storage.cuda(local_rank), avoid default all on cuda(0). w/o cuda will be load on CPU
            ckpt = torch.load(path_ckpt_file, map_location=lambda storage, loc: storage)
            # self.model.load_state_dict({f'module.{k}': v for k, v in ckpt['state_dict'].items()})
            # self.model.load_state_dict({k.replace('module.', ''): v for k, v in ckpt['state_dict'].items()})
            self.model.load_state_dict(ckpt['state_dict'])
            if 'extra' not in ckpt.keys() and 'extras' not in ckpt.keys():
                cfg.LOG.INS.warning(f'Loading third-party model {path_ckpt_file.split("/").pop()}')
                return  # not zl-ckpt format
            extra = ckpt['extra'] if 'extra' in ckpt else ckpt['extras']
            self._start_epoch = extra['epoch'] + 1
            self.global_step = extra['step'] if 'step' in extra else extra['steps']
            accuracy = extra['accuracy'] if 'accuracy' in extra else extra['perf_AP']
            cfg.LOG.INS.info(f"Loading {len(ckpt['state_dict'].keys())} keys from {path_ckpt_file.split('/').pop()} "
                f"(epoch {self._start_epoch - 1}, step {self.global_step}, accuracy {accuracy:.5f})")
            if cfg.ZL != 0:
                return
            self.optimizer.load_state_dict(ckpt['optimizer'])
            if cfg.FEAT.AMP and 'amp' in ckpt.keys():
                self._scaler.load_state_dict(ckpt['amp'])
            if os.path.exists(path_best_ckpt_file):
                ckpt = torch.load(path_best_ckpt_file, map_location=lambda storage, loc: storage)
                extra = ckpt['extra'] if 'extra' in ckpt else ckpt['extras']
                self._best_accuracy = extra['accuracy'] if 'accuracy' in extra else ['perf_AP']
        else:
            assert not (cfg.ZL != 0), Logger.zstr(
                f'No checkpoint found for EVAL {path_ckpt_file}. '
                f'You are using zid_{cfg.AIEI.EXP_ZID} {cfg.LOG.PATH_ZID.split("/").pop()}. '
                f'Try to change zid_{cfg.AIEI.EXP_ZID} in zlogs/zlogs.json or put ckpt.pth.tar into ckpt folder.',
                Logger.COLOR.ASSERT)

    def _train_epoch(self, epoch):
        extra = {}
        time_model_meter = mix.AverageMeter()  # w/o data_loader time
        time_data_meter = mix.AverageMeter()
        losses_meter = mix.AverageMeter()
        num_steps = len(self._train_loader)
        model_params = filter(lambda p: p.requires_grad, self.model.parameters())
        self.model.train()
        time_data = time.perf_counter()
        for step, batch_data in enumerate(self._train_loader):
            cost_time_data = time.perf_counter() - time_data
            time_model = time.perf_counter()
            with amp.autocast(enabled=cfg.FEAT.AMP):
                loss, ext_msg = self.on_train_step(step, batch_data)
            self._scaler.scale(loss).backward()
            if cfg.FEAT.GRAD_CLIP.MAX_NORM is not None or cfg.FEAT.GRAD_CLIP.CLIP_VALUE is not None:
                self._scaler.unscale_(self.optimizer)
                _feat_grad_clip(model_params)
            self._scaler.step(self.optimizer)
            self._scaler.update()
            self.optimizer.zero_grad()
            if torch.isinf(loss).any() or torch.isnan(loss).any():
                for name, param in self.model.named_parameters():
                    if torch.isinf(param.data).any() or torch.isnan(param.data).any():
                        print(param.data, Logger.zstr('INF or NaN data FOUND! ', Logger.COLOR.RED), name)
                    if torch.isinf(param.grad).any() or torch.isnan(param.grad).any():
                        print(param.grad, Logger.zstr('INF or NaN gradient FOUND! ', Logger.COLOR.RED), name)
                raise FloatingPointError(Logger.zstr(f'Loss became INF or NaN at epoch{epoch} step{step}!', Logger.COLOR.RED))
            if self.global_step < cfg.FEAT.WARM_UP_LR.STEP:  # use warm-up lr
                lr_scale = min(1., float(self.global_step + 1) / cfg.FEAT.WARM_UP_LR.STEP)
                for pg in self.optimizer.param_groups:
                    pg['lr'] = lr_scale * cfg.TRAIN.LR
            # utils.dist.average_gradients(model)
            # torch.cuda.synchronize(cfg.LOCAL_RANK)

            if step > 5 and cfg.AIEI.LOCAL_RANK == 0:  # initial meter value is large
                # on_train_step may have extra LOG.FREQ, impact speed. So drop (step % logger_freq == 0) when update meter
                if step % cfg.LOG.FREQ != 0:
                    losses_meter.update(loss.item())
                    time_model_meter.update(time.perf_counter() - time_model)
                    time_data_meter.update(cost_time_data * 1000)
                else:
                    # len(last_batch) may not equal _cfg.BATCH_SIZE
                    cur_speed = cfg.AIEI.WORLD_SIZE * cfg.TRAIN.BATCH_SIZE / time_model_meter.value
                    avg_speed = cfg.AIEI.WORLD_SIZE * cfg.TRAIN.BATCH_SIZE / time_model_meter.avg
                    left_epochs = (1 - step / len(self._train_loader)) + (cfg.TRAIN.EPOCHS - 1 - epoch)
                    total_samples = len(self._train_loader.sampler) * cfg.AIEI.WORLD_SIZE
                    msg = f'Epoch [{epoch}][{step}/{len(self._train_loader)}], ' \
                        f'LR {[round(group["lr"], 5) for group in self.optimizer.param_groups]}, ' \
                        f'Data {time_data_meter.value:.2f}({time_data_meter.avg:.2f}), ' \
                        f'Speed {cur_speed:.1f}({avg_speed:.1f}), ' \
                        f'ETA {total_samples / avg_speed * left_epochs / 3600:.2f}(h), ' \
                        f'Loss {losses_meter.value:.5f}({losses_meter.avg:.5f}), {ext_msg}'
                    cfg.LOG.INS.info(msg)
                    self.writer.add_scalar('train/loss', losses_meter.value, self.global_step)
            self.global_step += 1
            time_data = time.perf_counter()
            if step == num_steps // 2:
                extra['gpu_info'] = mix.get_gpu_info()
            # empty cache before eval in train (need last few steps, NOT last step)
            # or else gpu memory will increase to [train + eval], especially AMP mode
            if step > num_steps - 5:
                torch.cuda.empty_cache()
        return extra

    def _start_train(self):
        train_start_time = time.perf_counter()
        for epoch in range(self._start_epoch, cfg.TRAIN.EPOCHS):
            self.on_epoch(epoch)
            if epoch == 0 and cfg.AIEI.LOCAL_RANK == 0 and 'debug' not in cfg.AIEI.EXP_ZID:
                mix.bak_src_zip(cfg.LOG.PATH_ZID)
            if epoch != 0 and epoch % cfg.LOG.FREQ == 0:
                mix.copy_file(f'{cfg.LOG.PATH_ZID}/ckpt/ckpt.pth.tar', f'{cfg.LOG.PATH_ZID}/ckpt/ckpt_bak.pth.tar',
                    cfg.AIEI.LOCAL_RANK)

            if cfg.AIEI.DISTRIBUTED:
                self._train_loader.sampler.set_epoch(epoch)
            cfg.LOG.INS.info(
                f'Epoch {epoch}/{cfg.TRAIN.EPOCHS}, Step {self.global_step}/{len(self._train_loader) * cfg.TRAIN.EPOCHS}')
            time_epoch_start = time.perf_counter()
            extra_train = self._train_epoch(epoch)
            time_epoch_cost = time.perf_counter() - time_epoch_start
            cfg.LOG.INS.info(f'Train GPU Info: {extra_train["gpu_info"]}, Time: {time_epoch_cost:.2f}s, '
                f'Total Speed: {len(self._train_loader.sampler) * cfg.AIEI.WORLD_SIZE / time_epoch_cost:.1f}sps')
            if self.global_step >= cfg.FEAT.WARM_UP_LR.STEP:  # warm-up lr is finished, start self._lr_scheduler
                self._lr_scheduler.step()

            accuracy = 0.
            if cfg.TRAIN.EVAL_FREQ != 0 and (epoch % cfg.TRAIN.EVAL_FREQ == 0 or epoch == cfg.TRAIN.EPOCHS - 1):
                try:
                    extra_eval = self._start_eval(epoch)
                    accuracy = extra_eval['accuracy']
                except Exception as e:
                    cfg.LOG.INS.exception(e)
            if cfg.AIEI.LOCAL_RANK == 0:
                if accuracy > self._best_accuracy:
                    self._best_epoch = epoch
                    self._best_accuracy = accuracy
                    is_best_model = True
                else:
                    is_best_model = False
                save_ckpt_dict = {
                    'state_dict': self.model.state_dict(), 'optimizer': self.optimizer.state_dict(), 'extra':
                    {'epoch': epoch, 'step': self.global_step, 'accuracy': accuracy}
                }
                if cfg.FEAT.AMP:
                    save_ckpt_dict['amp'] = self._scaler.state_dict()
                zl_info = {
                    'host_name': socket.gethostname(), 'epoch': epoch, 'accuracy': accuracy, 'best_epoch': self._best_epoch,
                    'best_accuracy': self._best_accuracy, 'others': self.on_saved_info()
                }
                mix.save_checkpoint(save_ckpt_dict, is_best_model, f'{cfg.LOG.PATH_ZID}/ckpt', zl_info)
        if cfg.AIEI.LOCAL_RANK == 0:
            path_final_state_file = f'{cfg.LOG.PATH_ZID}/ckpt/final.pth'
            cfg.LOG.INS.info(f'Total cost time {(time.perf_counter() - train_start_time) / 3600:.2f} hours. '
                f'Saving final model state to {path_final_state_file}')
            torch.save(self.model.module.state_dict(), path_final_state_file)
            path_bak_ckpt_file = f'{cfg.LOG.PATH_ZID}/ckpt/ckpt_bak.pth.tar'
            if os.path.exists(path_bak_ckpt_file):
                os.remove(path_bak_ckpt_file)

    def _start_eval(self, epoch=-1):
        extra = {}
        try:
            if cfg.ZL != 0 and self.et_summary_input() is not None:
                summary.summary2(self.model, self.et_summary_input(), cfg.LOG.INS)
        except Exception as e:
            print(mix.get_exc_info())
        if epoch == -1:  # same to ZL != 0
            self.on_epoch(epoch)
        all_results = []
        eval_loader = self._eval_loader  # required, because of tqdm
        # num_samples are equal in all cards, so data replication exist when gather, that is len(results) >= real_total_samples
        num_steps, num_samples = len(eval_loader), len(eval_loader.sampler)
        batch_time = mix.AverageMeter()
        self.model.eval()
        with torch.no_grad():
            if cfg.AIEI.LOCAL_RANK == 0:
                eval_loader = tqdm(eval_loader)
            len_loader = len(eval_loader)
            start_time = time.perf_counter()  # time with loading data
            for step, batch_data in enumerate(eval_loader):
                end_t = time.perf_counter()  # user eval_step time
                with amp.autocast(enabled=cfg.FEAT.AMP):
                    result, ext_msg = self.on_eval_step(step, batch_data)
                if len_loader // 10 < step:  # < 9 * len_loader // 10:  # [1/10, 9/10]
                    batch_time.update(time.perf_counter() - end_t)
                all_results.append(result)
                if step == num_steps // 2:
                    extra['gpu_info'] = mix.get_gpu_info()
                if step > num_steps - 5:
                    torch.cuda.empty_cache()
            total_time = time.perf_counter() - start_time
            batch_size = cfg.EVAL.BATCH_SIZE if cfg.EVAL.BATCH_SIZE is not None else cfg.TRAIN.BATCH_SIZE
            cfg.LOG.INS.info(f'Eval GPU Info: {extra["gpu_info"]}, Time: {total_time:.2f}s, '
                f'Total Speed: {cfg.AIEI.WORLD_SIZE * num_samples / (total_time + 1e-12):.1f}fps, '
                f'Pure Speed: {batch_size / (batch_time.avg + 1e-12):.1f}fps')  # on_eval_step speed
        extra['accuracy'] = self.on_eval_end(epoch, all_results)
        return extra

    def start(self):
        pr = None
        if cfg.FEAT.PROFILE and cfg.AIEI.LOCAL_RANK == 0:
            pr = cProfile.Profile()
            pr.enable()
        if cfg.ZL == 0:
            self._start_train()
        else:
            self._start_eval()
        cfg.LOG.INS.blank_line()  # all end
        if pr is not None:
            pr.disable()
            pr.dump_stats(f'{cfg.LOG.PATH_ZID}/profile.prof')
            os.system(f'cd {cfg.LOG.PATH_ZID}; flameprof profile.prof > profile.svg; rm profile.prof')
            cfg.LOG.INS.info(
                f'profile.svg have saved in {cfg.LOG.PATH_ZID}. Use browser to visualize it. '
                f'You can also use @mix.profile to profile single method.', False)

    def epoch2step(self, epoch_float):  # approximately
        # len(train_loader): iterations per epoch, len(train_loader.sampler) == len(train_sampler):
        #  total samples per card (world_size)
        return int(len(self._train_loader) * epoch_float)

    # epoch == -1: can be regarded as on_eval_start
    # epoch == 0: can be regarded as on_train_start
    def on_epoch(self, epoch):
        pass

    def on_train_step(self, step, batch_data):
        return None, None

    def on_train_end(self):
        pass

    def on_eval_step(self, step, batch_data):
        return None, None

    def on_eval_end(self, epoch, all_results):
        return 0

    def on_saved_info(self):
        return None

    def et_scheduler(self, lr_last_epoch):
        return None

    def et_summary_input(self):
        return None  # return (torch.ones(2, 3, *cfg.INPUT_SHAPE).cuda(), )

    def write_graph(self, inputs):
        try:
            if self.writer is not None:
                self.writer.add_graph(self.model, (inputs, ))
        except Exception as e:
            print(e)
