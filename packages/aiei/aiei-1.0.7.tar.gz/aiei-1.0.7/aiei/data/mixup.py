# https://github.com/dmlc/gluon-cv/blob/49be01910a8e8424b017ed3df65c4928fc918c67/gluoncv/data/mixup/detection.py
from __future__ import absolute_import
import numpy as np
from torch.utils.data import Dataset


# 适用于Bottom-up
class Mixup(Dataset):
    def __init__(self, dataset):
        self.ds = dataset

    def __len__(self):
        return len(self.ds)

    def __getitem__(self, idx):
        # first image
        img1, label1 = self.ds[idx]
        lambd = 1

        if lambd >= 1:
            weights1 = np.ones((label1.shape[0], 1))
            label1 = np.hstack((label1, weights1))
            return img1, label1

        # second image
        idx2 = np.random.choice(np.delete(np.arange(len(self)), idx))
        img2, label2 = self.ds[idx2]

        # mixup two images
        height = max(img1.shape[0], img2.shape[0])
        width = max(img1.shape[1], img2.shape[1])
        mix_img = np.zeros(shape=(height, width, 3), dtype='float32')
        mix_img[:img1.shape[0], :img1.shape[1], :] = img1.astype('float32') * lambd
        mix_img[:img2.shape[0], :img2.shape[1], :] += img2.astype('float32') * (1. - lambd)
        mix_img = mix_img.astype('uint8')
        y1 = np.hstack((label1, np.full((label1.shape[0], 1), lambd)))
        y2 = np.hstack((label2, np.full((label2.shape[0], 1), 1. - lambd)))
        mix_label = np.vstack((y1, y2))
        return mix_img, mix_label
