import torch


class Key(object):
    ZL = 'zl'  # name to avoid many args/kwargs in code
    IMAGE = 'image'
    MASK = 'mask'
    COORD = 'coord'
    BOX = 'box'
    KEYPOINT = 'keypoint'

    # TODO USER: When add new transforms, also need to add them here, function name should be like 'self.apply_{SUPPORT_TRANS[i]}'
    # {'func_name': 'self.apply_box', 'list_func_name': 'self.apply_box_list'},
    SUPPORT_TRANS = [IMAGE, MASK, COORD, BOX, KEYPOINT]

    @staticmethod
    def get_support_args():
        list_value = list(Key.__dict__.values())
        return [value for value in list_value if isinstance(value, str) and '__' not in value]


class Compose(object):
    def __init__(self, transforms):
        self.transforms = transforms
        self.support_args = Key.get_support_args()

    def __call__(self, **kwargs):
        """
        :param kwargs: refer to `support_args`
        :return: kwargs keys same to `support_args`
        """
        # inspect.getfullargspec(self.__call__).args can get func args. e.g.: ['self', 'image', 'box', 'mask', 'keypoint']
        for key in kwargs.keys():
            assert key in self.support_args, f'not support "{key}". args should be {self.support_args}'
        for t in self.transforms:
            kwargs = t(kwargs)
        return kwargs

    def __repr__(self):
        format_string = f'\nTransform {self.__class__.__name__}(['
        for t in self.transforms:
            format_string += f'\n  {t},'
        format_string += '\n])'
        return format_string


class BaseTrans(object):
    def __call__(self, dict_args):
        tmp = self.apply_zl(dict_args[Key.ZL] if Key.ZL in dict_args else None)
        if tmp is not None:
            dict_args[Key.ZL] = tmp
        for key in Key.SUPPORT_TRANS:
            if key in dict_args:
                arg = dict_args[key]
                if isinstance(arg, (list, torch.Tensor)) and key not in [Key.IMAGE]:
                    tmp = eval(f'self.apply_list_{key}')(arg)
                else:
                    tmp = eval(f'self.apply_{key}')(arg)
                if tmp is not None:
                    dict_args[key] = tmp
        return dict_args

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'

    def apply_zl(self, zl):
        """
        Also resident executive function
        :param zl: forward zl
        :return: zl: can forward to next transform
        """
        return None

    def apply_image(self, image):
        """
        :param image: (ndarray)
        :return: image: (ndarray)
        """
        return None

    def apply_mask(self, mask):
        """
        :param mask: (ndarray)
        :return: mask: (ndarray)
        """
        return None

    def apply_list_mask(self, list_mask):
        """
        :param list_mask: (list|torch.Tensor), e.g. [(192, 256), (256, 256), ...] or tensor(num, h, w)
        :return: same to input
        """
        return None

    def apply_coord(self, coords):
        """
        :param coords: (ndarray) [..., 2], MODE_([x0, y0], [x1, y1], [x2, y2], [x3, y3], ...)
        :return: coords: (ndarray) [..., 2], MODE_([x0, y0], [x1, y1], [x2, y2], [x3, y3], ...)
        """
        return None

    def apply_list_coord(self, list_coords):
        """
        :param list_coords: (list) [(5, 2), (12, 2), ...]
        :return: list_coords: (list) [(5, 2), (12, 2), ...]
        """
        return None

    def apply_box(self, boxes):
        """
        :param boxes: (ndarray) (num, 4, 2), MODE_([x0, y0], [x1, y0], [x0, y1], [x1, y1])
        :return: boxes: (ndarray) (num, 4, 2), MODE_([x0, y0], [x1, y0], [x0, y1], [x1, y1])
        """
        return None

    def apply_keypoint(self, keypoints):
        """
        :param keypoints: (ndarray) (num, 17, 2 or 3), MODE_(x0, y0, vis)
        :return: keypoints: (ndarray) (num, 17, 2 or 3), MODE_(x0, y0, vis)
        """
        return None
