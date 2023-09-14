import cv2
import numpy as np
import torch
from torch.nn import functional as nn_fn
from .base_cls import BaseTrans
from .base_fn import affine_coord, get_affine_transform


def get_center_affine_transform(center, scale, output_size, inverse=False):
    if not isinstance(scale, np.ndarray) and not isinstance(scale, list):
        scale = np.array([scale, scale], dtype=np.float32)
    src = np.zeros((3, 2), dtype=np.float32)
    src_w = scale[0]
    src_dir = [0, src_w * -0.5]
    src[0, :] = center
    src[1, :] = src[0, :] + src_dir
    src[2, :] = src[1, :] + (src_dir[1], -src_dir[0])
    dst = np.zeros((3, 2), dtype=np.float32)
    dst_w, dst_h = output_size
    dst_dir = [0, dst_w * -0.5]
    dst[0, :] = [dst_w * 0.5, dst_h * 0.5]
    dst[1, :] = dst[0, :] + dst_dir
    dst[2, :] = dst[1, :] + (dst_dir[1], -dst_dir[0])
    tmp_list = [np.float32(src), np.float32(dst)]
    if inverse:
        tmp_list = tmp_list[::-1]
    trans = cv2.getAffineTransform(tmp_list[0], tmp_list[1])
    return trans


# https://github.com/kornia/kornia/blob/master/kornia/geometry/transform/imgwarp.py
def warp_affine(src, M, dsize, flags='bilinear', padding_mode='zeros'):
    # Applies an affine transformation to a tensor.
    # src (B, C, H, W), M ((B, 2, 3)), dsize (h, w), flags ('bilinear' | 'nearest'),
    #  padding_mode ('zeros' | 'border' | 'reflection')
    def convert_affine_matrix_to_homography(A):
        # Function that converts batch of affine matrices from [Bx2x3] to [Bx3x3].
        H: torch.Tensor = torch.nn.functional.pad(A, [0, 0, 0, 1], "constant", value=0.)
        H[..., -1, -1] += 1.0
        return H

    def src_norm_to_dst_norm(dst_pix_trans_src_pix, dsize_src, dsize_dst):
        def normal_transform_pixel(height, width):
            tr_mat = torch.tensor([[1.0, 0.0, -1.0], [0.0, 1.0, -1.0], [0.0, 0.0, 1.0]])  # 1x3x3
            tr_mat[0, 0] = tr_mat[0, 0] * 2.0 / (width - 1.0)
            tr_mat[1, 1] = tr_mat[1, 1] * 2.0 / (height - 1.0)
            tr_mat = tr_mat.unsqueeze(0)
            return tr_mat

        # source and destination sizes
        src_h, src_w = dsize_src
        dst_h, dst_w = dsize_dst
        # the devices and types
        device: torch.device = dst_pix_trans_src_pix.device
        dtype: torch.dtype = dst_pix_trans_src_pix.dtype
        # compute the transformation pixel/norm for src/dst
        src_norm_trans_src_pix = normal_transform_pixel(src_h, src_w).to(device, dtype)
        src_pix_trans_src_norm = torch.inverse(src_norm_trans_src_pix)
        dst_norm_trans_dst_pix = normal_transform_pixel(dst_h, dst_w).to(device, dtype)
        # compute chain transformations
        in_dst_norm_trans_src_norm = (dst_norm_trans_dst_pix @ (dst_pix_trans_src_pix @ src_pix_trans_src_norm))
        return in_dst_norm_trans_src_norm

    if not len(src.shape) == 4:
        raise ValueError(f'Input src must be a BxCxHxW tensor. Got {src.shape}')
    if not (len(M.shape) == 3 or M.shape[-2:] == (2, 3)):
        raise ValueError(f'Input M must be a Bx2x3 tensor. Got {M.shape}')
    B, C, H, W = src.size()
    dsize_src = (H, W)
    out_size = dsize
    # we generate a 3x3 transformation matrix from 2x3 affine
    M_3x3 = convert_affine_matrix_to_homography(M)
    dst_norm_trans_src_norm = src_norm_to_dst_norm(M_3x3, dsize_src, out_size)
    src_norm_trans_dst_norm = torch.inverse(dst_norm_trans_src_norm)
    grid = nn_fn.affine_grid(src_norm_trans_dst_norm[:, :2, :], [B, C, out_size[0], out_size[1]], align_corners=True)
    result = nn_fn.grid_sample(src.float(), grid.float(), mode=flags, padding_mode=padding_mode, align_corners=True)
    return result


class RandomAffine(BaseTrans):
    def __init__(self, dst_size=(-1, -1), min_scale=1., max_scale=1., max_translate=0, max_rotation=0, scale_type='long'):
        self.dst_size = dst_size  # image dst_size (w, h)
        self.max_rotation = max_rotation
        self.max_translate = max_translate
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.scale_type = scale_type
        self.affine_mat = None

    def apply_zl(self, zl):
        if 'cs' in zl:
            center, scale = zl['cs']
        else:
            src_height, src_width = zl['src_size']  # (648, 568)
            center = np.array((src_width / 2, src_height / 2))
            scale = min(src_width, src_height) if self.scale_type == 'short' else max(src_width, src_height)
        aug_scale = scale * (np.random.random() * (self.max_scale - self.min_scale) + self.min_scale)
        # aug_scale = scale * np.random.choice(np.arange(self.min_scale, self.max_scale, 0.1))
        # aug_scale = scale * np.clip(np.random.randn() * scale_factor + 1, 1 - scale_factor, 1 + scale_factor)
        aug_rot = (np.random.random() * 2 - 1) * self.max_rotation  # if random.random() <= prob_rotation else 0
        dx = np.random.randint(-self.max_translate, self.max_translate) if self.max_translate > 0 else 0
        dy = np.random.randint(-self.max_translate, self.max_translate) if self.max_translate > 0 else 0
        aug_shift = np.array([dx / 200., dy / 200.], dtype=np.float32)
        # use user define random method to override the default. __init__ only need param: dst_size
        if 'aug_scale' in zl:
            aug_scale = zl['aug_scale']
        if 'aug_rot' in zl:
            aug_rot = zl['aug_rot']
        if 'aug_shift' in zl:
            aug_shift = zl['aug_shift']
        if 'dst_size' in zl:  # for group, from ResizeEdge
            self.dst_size = zl['dst_size']
        self.affine_mat = get_affine_transform(center, aug_scale, self.dst_size, aug_rot, aug_shift)
        return zl

    def apply_image(self, image):
        image = cv2.warpAffine(image, self.affine_mat, self.dst_size, flags=cv2.INTER_LINEAR)
        return image

    def apply_mask(self, mask):
        mask = cv2.warpAffine(mask, self.affine_mat, self.dst_size, flags=cv2.INTER_LINEAR)  # support (H, W, C), C > 3
        return mask

    # TODO: REMOVE IT TO SIMPLIFY
    def apply_list_mask(self, list_mask):
        if isinstance(list_mask, torch.Tensor):  # FloatTensor
            affine_mat = torch.from_numpy(self.affine_mat).unsqueeze(0)  # (B, 2, 3)
            result = warp_affine(list_mask.unsqueeze(0), affine_mat, (self.dst_size[1], self.dst_size[0]))  # (B, C, H, W)
            return result.squeeze(0)
        for i, mask in enumerate(list_mask):
            list_mask[i] = self.apply_mask(mask)
        return list_mask

    def apply_coord(self, coords, is_clip=True):
        coords = affine_coord(coords, self.affine_mat)
        if is_clip:
            coords[..., 0] = np.clip(coords[..., 0], 0, self.dst_size[0] - 1)  # clip to [0, w - 1]
            coords[..., 1] = np.clip(coords[..., 1], 0, self.dst_size[1] - 1)
        return coords

    def apply_list_coord(self, list_coords):
        for i, coords in enumerate(list_coords):
            list_coords[i] = self.apply_coord(coords)
        return list_coords

    def apply_box(self, boxes):
        return self.apply_coord(boxes)

    def apply_keypoint(self, keypoints):
        keypoints[..., :2] = affine_coord(keypoints[..., :2], self.affine_mat)
        return keypoints
