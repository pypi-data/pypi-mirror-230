import numpy as np
import torch
import torch.nn as nn
from torch.nn import functional as nn_fn


def topk_np(array, k):
    idx = np.argpartition(array, -k)[-k:]  # Indices not sorted
    idx = idx[np.argsort(array[idx])][::-1]  # Indices sorted by value from largest to smallest
    return array[idx], idx


def softmax_np(x):
    x_row_max = x.max(axis=-1)
    x_row_max = x_row_max.reshape(list(x.shape)[:-1] + [1])
    x = x - x_row_max
    x_exp = np.exp(x)
    x_exp_row_sum = x_exp.sum(axis=-1).reshape(list(x.shape)[:-1] + [1])
    softmax = x_exp / x_exp_row_sum
    return softmax


def pseudo_nms(fmap, pool_size=5):
    pad = (pool_size - 1) // 2
    fmap_max = nn_fn.max_pool2d(fmap, pool_size, stride=1, padding=pad)
    keep = torch.eq(fmap_max, fmap).float()
    return fmap * keep


def fixed_padding(inputs, kernel_size, dilation):
    kernel_size_effective = kernel_size + (kernel_size - 1) * (dilation - 1)
    pad_total = kernel_size_effective - 1
    pad_beg = pad_total // 2
    pad_end = pad_total - pad_beg
    padded_inputs = nn_fn.pad(inputs, (pad_beg, pad_end, pad_beg, pad_end))
    return padded_inputs
