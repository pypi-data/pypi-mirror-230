import numpy as np
from .base_cls import BaseTrans
from .base_fn import blend


# support NCHW/CHW/HWC
class RandomBrightness(BaseTrans):
    def __init__(self, intensity_min, intensity_max):
        self.intensity_min = intensity_min
        self.intensity_max = intensity_max
        self.random_weight = None

    def apply_zl(self, zl):
        self.random_weight = np.random.uniform(self.intensity_min, self.intensity_max)

    def apply_image(self, image):
        image = blend(image, 0, 1 - self.random_weight, self.random_weight)
        return image
