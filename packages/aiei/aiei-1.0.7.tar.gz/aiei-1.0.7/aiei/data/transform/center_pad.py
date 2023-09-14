import torch
import cv2
import numpy as np
from .base_cls import BaseTrans
from .base_fn import affine_coord, get_affine_transform
from .random_affine import warp_affine


def get_scale_pad(img=None, src_size=None, scale_factor=1.0, pad=None, dst_size=None, scale_type='center_inside'):
    # center pad or generate different scale target, ndarray
    pad = pad - 1  # e.g.: pad = 63
    if img is not None:
        src_height, src_width = img.shape[:2]
    elif src_size is not None:
        src_width, src_height = src_size
    else:
        raise ValueError('img and src_size cannot be None at the same time')
    new_width = int(src_width * scale_factor)
    new_height = int(src_height * scale_factor)

    if dst_size is not None:  # output fix resolution
        assert scale_type in ['center_inside', 'center_crop']
        if pad is None:  # no pad
            inp_width, inp_height = dst_size
        else:
            inp_width = (dst_size[0] | pad) + 1
            inp_height = (dst_size[1] | pad) + 1
        center = np.array([new_width / 2. + 0.5, new_height / 2. + 0.5], dtype=np.float32)
        s = max(inp_width, inp_height) if scale_type == 'center_inside' else min(inp_width,
            inp_height)  # center_inside or center_crop
        scale = np.array([s, s], dtype=np.float32)
    else:  # output keep resolution
        assert pad is not None, 'pad should not be None'
        inp_width = (new_width | pad) + 1  # same to (x + 63) // 64 * 64
        inp_height = (new_height | pad) + 1  # the smallest number that can be divisible by (pad + 1)
        center = np.array([new_width / 2. + 0.5, new_height / 2. + 0.5], dtype=np.float32)
        scale = np.array([inp_width, inp_height], dtype=np.float32)

    transform = get_affine_transform(center, scale, output_size=(inp_width, inp_height), inverse=False)
    center /= scale_factor  # for multi-scale inverse transform
    scale /= scale_factor
    if img is not None:
        resized_img = cv2.resize(img, (new_width, new_height))  # scale img
        img = cv2.warpAffine(resized_img, transform, (inp_width, inp_height))  # transform img
        return img, center, scale
    return transform, (inp_width, inp_height)


class CenterPad(BaseTrans):
    def __init__(self, dst_size=None, pad=32, scale_type='center_inside'):
        assert scale_type in ['center_inside', 'center_crop']
        self.dst_size = dst_size  # (w, h) it can also be set in init or apply_zl, dst_size will be padded (if not None)
        self.src_size = None  # (w, h)
        self.pad = pad
        self.scale_type = scale_type
        self.affine_mat = None

    def apply_zl(self, zl):
        self.src_size = zl['src_size']
        if 'dst_size' in zl:
            self.dst_size = zl['dst_size']
        self.affine_mat, self.dst_size = get_scale_pad(src_size=self.src_size, pad=self.pad, dst_size=self.dst_size,
            scale_type=self.scale_type)
        assert self.dst_size is not None, f'self.dst_size={self.dst_size} is an unexpected value'
        return zl

    def apply_image(self, image):
        return cv2.warpAffine(image, self.affine_mat, self.dst_size, flags=cv2.INTER_LINEAR)

    def apply_mask(self, mask):
        return self.apply_image(mask)

    def apply_list_mask(self, list_mask):
        if isinstance(list_mask, torch.Tensor):
            affine_mat = torch.from_numpy(self.affine_mat).unsqueeze(0)  # (B, 2, 3)
            result = warp_affine(list_mask.unsqueeze(0), affine_mat, (self.dst_size[1], self.dst_size[0]))  # (B, C, H, W)
            return result.squeeze(0)
        for i, mask in enumerate(list_mask):
            list_mask[i] = self.apply_mask(mask)
        return list_mask

    def apply_coord(self, coords, is_clip=True):
        coords = affine_coord(coords, self.affine_mat)
        if is_clip:
            coords[..., 0] = np.clip(coords[..., 0], 0, self.dst_size[0] - 1)
            coords[..., 1] = np.clip(coords[..., 1], 0, self.dst_size[1] - 1)
        return coords

    def apply_list_coord(self, list_coords):
        for i, coords in enumerate(list_coords):
            list_coords[i] = self.apply_coord(coords)
        return list_coords

    def apply_box(self, boxes):
        return self.apply_coord(boxes)

    def apply_keypoint(self, keypoints, ind=0):
        keypoints[..., :2] = affine_coord(keypoints[..., :2], self.affine_mat)
        return keypoints
