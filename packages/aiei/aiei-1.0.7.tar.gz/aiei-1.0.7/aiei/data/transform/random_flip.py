import torch
import random
import cv2
import numpy as np
from .base_cls import BaseTrans


class RandomFlip(BaseTrans):
    def __init__(self, wh=None, prob=0.5, flip_type='hflip', **kwargs):
        support_kwargs = ['kp_flip_index']
        for key in kwargs:
            assert key in support_kwargs, f'not support {key}, arg should be one of {support_kwargs}'
        assert flip_type in ['hflip'], f'not support flip_type={flip_type}'
        self.wh = wh
        self.prob = prob
        self.kwargs = kwargs
        self.rand_num = None

    def apply_zl(self, zl):
        if 'wh' in zl:
            self.wh = zl['wh']
        self.rand_num = random.random()
        assert self.wh is not None, f'self.wh={self.wh} is an unexpected value'
        return zl

    def apply_image(self, image):
        if self.rand_num < self.prob:
            if isinstance(image, torch.Tensor):  # C, H, W (after ToTensor)
                return torch.flip(image, (-1, ))
            elif image.ndim == 3 and image.shape[2] > 1 and image.dtype == np.uint8:
                return cv2.flip(image, 1)  # Opencv is faster than numpy only in case of non-gray scale 8bits images
            else:
                return np.ascontiguousarray(image[:, ::-1])  # vflip: img[::-1]
        return image

    def apply_mask(self, mask):
        if self.rand_num < self.prob:
            return np.ascontiguousarray(mask[:, ::-1])  # vflip: img[::-1]
        return mask

    def apply_list_mask(self, list_mask):
        if isinstance(list_mask, torch.Tensor):
            return torch.flip(list_mask, (-1, )) if self.rand_num < self.prob else list_mask
        for i, mask in enumerate(list_mask):
            list_mask[i] = self.apply_mask(mask)
        return list_mask

    def apply_coord(self, coords):
        if self.rand_num < self.prob:
            coords[..., 0] = self.wh - coords[..., 0]
            coords[..., 0] = np.clip(coords[..., 0], 0, self.wh - 1)  # clip to [0, w - 1]
        return coords

    def apply_list_coord(self, list_coords):
        for i, coords in enumerate(list_coords):
            list_coords[i] = self.apply_coord(coords)
        return list_coords

    def apply_box(self, boxes, ind=0):
        if self.rand_num < self.prob:
            # Note: the inputs are floating point coordinates, not pixel indices.
            # Therefore they are flipped by `w - x`, not `w - x - 1`
            boxes[..., 0] = self.wh - boxes[..., 0]  # result (R, T, L, D), that's (right-top, left-down)
            boxes = boxes[:, [2, 1, 0, 3]]  # change (R, T, L, D) to (L, T, R, D)
            boxes[..., 0] = np.clip(boxes[..., 0], 0, self.wh - 1)  # clip to [0, w - 1]
        return boxes

    def apply_keypoint(self, keypoints, ind=0):
        # coco_kp_flip_index = [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15]
        if self.rand_num < self.prob:
            keypoints[..., 0] = self.wh - keypoints[..., 0] - 1
            keypoints = keypoints[:, self.kwargs['kp_flip_index']]
        return keypoints
