from torchvision.transforms import functional as tv_fn
from .base_cls import BaseTrans


class Normalize(BaseTrans):
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def apply_image(self, image):
        image = tv_fn.normalize(image, mean=self.mean, std=self.std)
        return image
