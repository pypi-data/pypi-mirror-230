import numpy as np
import cv2
import torch


# all is (w, h), not (h, w)
def get_affine_transform(center, scale, output_size, rot=0, shift=np.array([0, 0], dtype=np.float32), inverse=False):
    def get_3rd_point(a, b):
        direct = a - b
        return b + np.array([-direct[1], direct[0]], dtype=np.float32)

    if not isinstance(scale, np.ndarray) and not isinstance(scale, list):
        scale = np.array([scale, scale])
    src_w = scale[0]
    dst_w = output_size[0]
    dst_h = output_size[1]

    rot_rad = np.pi * rot / 180
    src_point = [0, src_w * -0.5]
    sn, cs = np.sin(rot_rad), np.cos(rot_rad)
    src_dir = [0, 0]
    src_dir[0] = src_point[0] * cs - src_point[1] * sn
    src_dir[1] = src_point[0] * sn + src_point[1] * cs
    dst_dir = np.array([0, dst_w * -0.5], np.float32)

    src = np.zeros((3, 2), dtype=np.float32)
    dst = np.zeros((3, 2), dtype=np.float32)
    src[0, :] = center + scale * shift
    src[1, :] = center + src_dir + scale * shift
    dst[0, :] = [dst_w * 0.5, dst_h * 0.5]
    dst[1, :] = np.array([dst_w * 0.5, dst_h * 0.5]) + dst_dir
    src[2:, :] = get_3rd_point(src[0, :], src[1, :])
    dst[2:, :] = get_3rd_point(dst[0, :], dst[1, :])

    tmp_list = [np.float32(src), np.float32(dst)]
    if inverse:
        tmp_list = tmp_list[::-1]
    trans = cv2.getAffineTransform(tmp_list[0], tmp_list[1])
    return trans


def affine_coord(coords, affine_mat):
    shape = coords.shape
    coords = coords.reshape(-1, 2)
    coords = np.column_stack((coords, np.ones(coords.shape[0])))
    coords = np.dot(coords, affine_mat.T).reshape(shape)  # 2 * 3 @ 3 * 1, 3: [x, y, 1]
    return coords


def blend(img, src_image, src_weight, dst_weight):
    if img.dtype == np.uint8:
        img = img.astype(np.float32)
        img = src_weight * src_image + dst_weight * img
        return np.clip(img, 0, 255).astype(np.uint8)
    else:  # float [0, 1]
        return src_weight * src_image + dst_weight * img


def get_multi_scale(img, short_size, scale_factor, pad):
    # center pad, with fix short_size
    src_height, src_width = img.shape[:2]
    new_width = int(src_width * scale_factor)
    new_height = int(src_height * scale_factor)
    center = np.array([new_width / 2.0 + 0.5, new_height / 2.0 + 0.5], dtype=np.float32)
    if new_width < new_height:  # + 63): similar to + 0.5,  // 64 * 64: ensure divisible by 64
        w_resized = short_size * scale_factor
        w_resized = int((w_resized + (pad - 1)) // pad * pad)
        h_resized = (new_height / new_width * short_size) * scale_factor
        h_resized = int((h_resized + (pad - 1)) // pad * pad)
        scale_w = new_width
        scale_h = h_resized / w_resized * new_width
    else:
        h_resized = short_size * scale_factor
        h_resized = int((h_resized + (pad - 1)) // pad * pad)
        w_resized = (new_width / new_height * short_size) * scale_factor
        w_resized = int((w_resized + (pad - 1)) // pad * pad)
        scale_h = new_height
        scale_w = w_resized / h_resized * new_height
    scale = np.array([scale_w, scale_h], dtype=np.float32)
    transform = get_affine_transform(center, scale, output_size=(w_resized, h_resized), inverse=False)
    img = cv2.resize(img, (int(new_width), int(new_height)))
    img = cv2.warpAffine(img, transform, (w_resized, h_resized))
    center /= scale_factor  # for multi-scale inverse transform
    scale /= scale_factor
    return img, center, scale


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


def get_simple_pad(list_img, dst_size=None, pad=32):
    # NOT CENTER PAD, only pad right/bottom. list_img: list_Tensor[(C, H, W), (C, H, W), ...], dst_size: (C, H, W)
    if isinstance(list_img, torch.Tensor) and len(list_img.shape) == 3:
        list_img = [list_img]
    if dst_size is None:
        assert len(list_img) == 1, 'dst_size is None, need len(list_img) == 1'
        dst_size = list_img[0].shape
    pad = pad - 1
    tmp_w = dst_size[-1] if dst_size[-1] % (pad + 1) == 0 else (dst_size[-1] | pad) + 1
    tmp_h = dst_size[-2] if dst_size[-2] % (pad + 1) == 0 else (dst_size[-2] | pad) + 1
    pad_img = list_img[0].new_full((len(list_img), dst_size[0], tmp_h, tmp_w),
        fill_value=0.)  # (B, C, H, W), same dtype/devic to list_img[0]
    for i, img in enumerate(list_img):
        pad_img[i, :, :img.shape[-2], :img.shape[-1]] = img
    return pad_img
