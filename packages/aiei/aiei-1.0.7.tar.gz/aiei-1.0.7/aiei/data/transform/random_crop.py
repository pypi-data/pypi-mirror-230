import numpy as np
from .base_cls import BaseTrans


def get_random_crop(src_size, crop_size, crop_type='absolute'):
    h, w = src_size
    if crop_type == 'relative':  # crop (H * CROP.SIZE[0], W * CROP.SIZE[1]) part of an input of size (H, W)
        ch, cw = crop_size
        crop_h, crop_w = int(h * ch + 0.5), int(w * cw + 0.5)
    elif crop_type == 'relative_range':  # uniformly sample relative crop size from between [CROP.SIZE[0], [CROP.SIZE[1]].
        # and [1, 1] and use it as in "relative" scenario.
        crop_size = np.asarray(crop_size, dtype=np.float32)
        ch, cw = crop_size + np.random.rand(2) * (1 - crop_size)
        crop_h, crop_w = int(h * ch + 0.5), int(w * cw + 0.5)
    else:  # crop_type == 'absolute':
        crop_h, crop_w = crop_size
    assert h >= crop_h and w >= crop_w
    y0 = np.random.randint(h - crop_h + 1)
    x0 = np.random.randint(w - crop_w + 1)
    return x0, y0, crop_w, crop_h


class RandomCrop(BaseTrans):
    def __init__(self, crop_size, crop_type='absolute'):
        self.crop_size = crop_size  # h, w
        self.crop_type = crop_type
        self.x0, self.y0, self.crop_w, self.crop_h = None, None, None, None

    def apply_zl(self, zl):
        self.x0, self.y0, self.crop_w, self.crop_h = get_random_crop(zl['src_size'], self.crop_size, self.crop_type)
        return zl

    def apply_image(self, image):
        if len(image.shape) <= 3:
            return image[self.y0:self.y0 + self.crop_h, self.x0:self.x0 + self.crop_w]
        else:
            return image[..., self.y0:self.y0 + self.crop_h, self.x0:self.x0 + self.crop_w, :]

    def apply_mask(self, mask):
        return mask[self.y0:self.y0 + self.crop_h, self.x0:self.x0 + self.crop_w]

    def apply_list_mask(self, list_mask):
        for i, mask in enumerate(list_mask):
            list_mask[i] = self.apply_mask(mask)
        return list_mask

    def apply_coord(self, coords):
        coords[..., 0] -= self.x0
        coords[..., 1] -= self.y0
        return coords

    def apply_list_coord(self, list_coords):
        for i, coords in enumerate(list_coords):
            list_coords[i] = self.apply_coord(coords)
        return list_coords

    def apply_box(self, boxes):
        return self.apply_coord(boxes)

    def apply_keypoint(self, keypoints):
        return self.apply_coord(keypoints)
