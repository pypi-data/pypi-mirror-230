import numpy as np
from .base_cls import BaseTrans
from .base_fn import blend


class RandomLighting(BaseTrans):
    """
    Randomly transforms image color using fixed PCA over ImageNet.
    """
    def __init__(self, scale):
        self.scale = scale
        self.eigen_vec = np.array([[-0.5675, 0.7192, 0.4009], [-0.5808, -0.0045, -0.8140], [-0.5836, -0.6948, 0.4203]])
        self.eigen_val = np.array([0.2175, 0.0188, 0.0045])
        self.random_weight = None

    def apply_zl(self, zl):
        self.random_weight = np.random.normal(scale=self.scale, size=3)  # the degree of color jittering

    def apply_image(self, image):
        assert image.shape[-1] == 3, 'Lighting only works on RGB images'
        image = blend(image, self.eigen_vec.dot(self.random_weight * self.eigen_val), 1.0, 1.0)
        return image
