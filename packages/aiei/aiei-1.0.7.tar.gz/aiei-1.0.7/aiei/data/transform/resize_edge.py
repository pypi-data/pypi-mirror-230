import sys
import cv2
import torch
import numpy as np
from torch.nn import functional as nn_fn
from .base_cls import BaseTrans


def get_random_resize_edge(src_size, edge_length, type_sample='choice', max_edge_length=sys.maxsize):
    # if max_edge_length != sys.maxsize is ResizeShortestEdge, else ResizeLongestEdge
    h, w = src_size
    assert type_sample in ['range', 'choice'], type_sample
    if isinstance(edge_length, int):
        edge_length = (edge_length, edge_length)
    size = np.random.choice(edge_length) if type_sample == 'choice' else np.random.randint(edge_length[0], edge_length[1] + 1)
    scale = size * 1.0 / (min(h, w) if max_edge_length != sys.maxsize else max(h, w))
    if max_edge_length != sys.maxsize:
        new_h, new_w = (size, scale * w) if h < w else (scale * h, size)
    else:
        new_h, new_w = (scale * h, size) if h < w else (size, scale * w)
    if max(new_h, new_w) > max_edge_length:  # for ResizeShortestEdge
        scale = max_edge_length * 1.0 / max(new_h, new_w)
        new_h = new_h * scale
        new_w = new_w * scale
    new_w = int(new_w + 0.5)
    new_h = int(new_h + 0.5)
    return new_w, new_h


class ResizeEdge(BaseTrans):
    def __init__(self, edge_length, type_sample='choice', max_edge_length=sys.maxsize):
        # if max_edge_length != sys.maxsize is ResizeShortestEdge (short edge in edge_length, long edge adaptive),
        #  else ResizeLongestEdge
        if not isinstance(edge_length, list):
            edge_length = [edge_length]
        self.edge_length = edge_length
        self.type_sample = type_sample
        self.max_edge_length = max_edge_length
        self.new_w, self.new_h = None, None
        self.src_width, self.src_height = None, None

    def apply_zl(self, zl):
        self.src_height, self.src_width = zl['src_size']  # (648, 568)
        self.new_w, self.new_h = get_random_resize_edge(zl['src_size'], self.edge_length, self.type_sample, self.max_edge_length)
        zl['dst_size'] = (self.new_w, self.new_h)  # forward to RandomAffine apply_zl
        return zl

    def apply_image(self, image):
        return cv2.resize(image, (self.new_w, self.new_h))  # bilinear

    def apply_mask(self, mask):
        return cv2.resize(mask, (self.new_w, self.new_h), interpolation=cv2.INTER_NEAREST)  # nearest

    def apply_list_mask(self, list_mask):
        if isinstance(list_mask, torch.Tensor):
            mask = nn_fn.interpolate(list_mask.unsqueeze(0), (self.new_h, self.new_w), mode='bilinear', align_corners=True)
            return mask.squeeze(0)
        for i, mask in enumerate(list_mask):
            list_mask[i] = self.apply_mask(mask)
        return list_mask

    def apply_coord(self, coords):
        coords[..., 0] = coords[..., 0] * (self.new_w / self.src_width)
        coords[..., 1] = coords[..., 1] * (self.new_h / self.src_height)
        return coords

    def apply_list_coord(self, list_coords):
        for i, coords in enumerate(list_coords):
            list_coords[i] = self.apply_coord(coords)
        return list_coords

    def apply_box(self, boxes):
        return self.apply_coord(boxes)

    def apply_keypoint(self, keypoints):
        return self.apply_coord(keypoints)
