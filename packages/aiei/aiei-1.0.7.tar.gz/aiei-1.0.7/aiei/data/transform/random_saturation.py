import numpy as np
from .base_cls import BaseTrans
from .base_fn import blend


class RandomSaturation(BaseTrans):
    def __init__(self, intensity_min, intensity_max):
        self.intensity_min = intensity_min
        self.intensity_max = intensity_max
        self.random_weight = None

    def apply_zl(self, zl):
        self.random_weight = np.random.uniform(self.intensity_min, self.intensity_max)

    def apply_image(self, image):
        assert image.shape[-1] == 3, 'Saturation only works on RGB images'
        grayscale = image.dot([0.299, 0.587, 0.114])[:, :, np.newaxis]
        image = blend(image, grayscale, 1 - self.random_weight, self.random_weight)
        return image
