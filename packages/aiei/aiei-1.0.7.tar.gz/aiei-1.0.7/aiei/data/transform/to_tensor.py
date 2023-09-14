from torchvision.transforms import functional as tv_fn
from .base_cls import BaseTrans


class ToTensor(BaseTrans):
    def apply_image(self, image):
        return tv_fn.to_tensor(image)
