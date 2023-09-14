import random
import math
import numpy as np
from .base_cls import BaseTrans


def get_random_erase(img, sl, sh, r, mean):
    img_h, img_w, img_c = img.shape
    for _ in range(20):
        area = img_h * img_w
        target_area = np.random.uniform(sl, sh) * area
        aspect_ratio = np.random.uniform(r, 1 / r)
        h = int(round(math.sqrt(target_area * aspect_ratio)))
        w = int(round(math.sqrt(target_area / aspect_ratio)))
        if w < img_w and h < img_h:
            x1 = np.random.randint(0, img_h - h)
            y1 = np.random.randint(0, img_w - w)
            if img_c == 3:
                img[x1:x1 + h, y1:y1 + w, 0] = mean[0]
                img[x1:x1 + h, y1:y1 + w, 1] = mean[1]
                img[x1:x1 + h, y1:y1 + w, 2] = mean[2]
            else:
                img[x1:x1 + h, y1:y1 + w] = mean[0]
            return img
    return img


class RandomErase(BaseTrans):
    """ Randomly selects a rectangle region in an image and erases its pixels.

    Args:
         prob: The probability that the Random Erasing operation will be performed.
         sl: Minimum proportion of erased area against input image.
         sh: Maximum proportion of erased area against input image.
         r: Minimum aspect ratio of erased area.
         mean: Erasing value.
    """
    def __init__(self, prob=0.5, sl=0.02, sh=0.4, r=0.3, mean=(0.485, 0.456, 0.406)):
        self.prob = prob
        self.sl = sl
        self.sh = sh
        self.r = r
        self.mean = mean
        self.rand_num = None

    def apply_zl(self, zl):
        self.rand_num = random.random()

    def apply_image(self, image):  # image: Tensor, place after Normalize
        if self.rand_num < self.prob:
            return get_random_erase(image, self.sl, self.sh, self.r, self.mean)
        return image
