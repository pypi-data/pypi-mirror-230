import numpy as np
import torch
from torch.nn import functional as nn_fn
from pycocotools import mask as pycoco_mask


def xywh_xy2(boxes):
    boxes[:, 2] += boxes[:, 0]
    boxes[:, 3] += boxes[:, 1]
    return boxes


def xy2_xywh(boxes):
    boxes[:, 2] -= boxes[:, 0]
    boxes[:, 3] -= boxes[:, 1]
    return boxes


def xy2_xy4(boxes):
    # Indexes of converting (x0, y0, x1, y1) box into 4 coordinates of ([x0, y0], [x1, y0], [x0, y1], [x1, y1]).
    idxs = np.array([(0, 1), (2, 1), (0, 3), (2, 3)]).flatten()
    boxes = np.asarray(boxes).reshape(-1, 4)[:, idxs].reshape(-1, 4, 2)
    return boxes


def xy4_xy2(boxes):
    min_xy = boxes.min(axis=1)
    max_xy = boxes.max(axis=1)
    boxes = np.concatenate((min_xy, max_xy), axis=1)
    return boxes


def box_area(boxes, keep_axis=False):
    x_min, y_min, x_max, y_max = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (y_max - y_min) * (x_max - x_min)
    if keep_axis:
        return areas[:, None]
    return areas


def polygon2mask(mask_ann, img_h, img_w):
    if isinstance(mask_ann, list):  # one polygon [22, 23, 24, 25...]
        # polygon -- a single object might consist of multiple parts, we merge all parts into one mask rle code
        rles = pycoco_mask.frPyObjects(mask_ann, img_h, img_w)
        rle = pycoco_mask.merge(rles)
    elif isinstance(mask_ann['counts'], list):
        # uncompressed RLE
        rle = pycoco_mask.frPyObjects(mask_ann, img_h, img_w)
    else:
        rle = mask_ann  # rle
    mask = pycoco_mask.decode(rle)
    return mask


def get_max_shape(list_shape):
    return list(max(s) for s in zip(*list_shape))
