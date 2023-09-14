import torch
import torch.nn as nn
import numpy as np
from torch.nn import functional as F


def softargmax2d(input, beta=100):
    *_, h, w = input.shape

    input = input.reshape(*_, h * w)
    input = nn.functional.softmax(beta * input, dim=-1)

    indices_c, indices_r = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h), indexing='xy')

    indices_r = torch.tensor(np.reshape(indices_r, (-1, h * w)))
    indices_c = torch.tensor(np.reshape(indices_c, (-1, h * w)))

    result_r = torch.sum((h - 1) * input * indices_r, dim=-1)
    result_c = torch.sum((w - 1) * input * indices_c, dim=-1)

    result = torch.stack([result_r, result_c], dim=-1)

    return result


def softargmax1d(input, beta=100):
    *_, n = input.shape
    input = nn.functional.softmax(beta * input, dim=-1)
    indices = torch.linspace(0, 1, n)
    result = torch.sum((n - 1) * input * indices, dim=-1)
    return result


class SoftArgMax1D(nn.Module):
    def __init__(self, base_index=0, step_size=1):
        super(SoftArgMax1D, self).__init__()
        self.base_index = base_index
        self.step_size = step_size
        self.softmax = torch.nn.Softmax(dim=1)

    def forward(self, x):
        """
        SoftArgMax(x) = \sum_i (i * softmax(x)_i)
        """
        smax = self.softmax(x)
        end_index = self.base_index + x.size()[1] * self.step_size
        indices = torch.arange(start=self.base_index, end=end_index, step=self.step_size)
        return torch.matmul(smax, indices)


class SoftArgMax2D(nn.Module):
    def __init__(self, cuda=True):
        super(SoftArgMax2D, self).__init__()
        self.cuda = cuda

    def forward(self, heatmaps):
        """
        SoftArgMax2d(x) = (\sum_i \sum_j (i * softmax2d(x)_ij), \sum_i \sum_j (j * softmax2d(x)_ij))
        """
        batch_size = heatmaps.shape[0]
        num_joints = heatmaps.shape[1]
        heighty = heatmaps.shape[2]
        widthx = heatmaps.shape[3]
        # need change x and y
        y = torch.arange(widthx)
        x = torch.arange(heighty)
        xx, yy = torch.meshgrid(x, y)
        xx = xx.float() + 1
        yy = yy.float() + 1

        # heat = heatmaps[0, -1].numpy()
        # yy_max, xx_max = np.unravel_index(heat.argmax(), heat.shape)
        # print(yy_max, xx_max, heat[yy_max][xx_max])
        heatmaps = heatmaps.reshape((batch_size, num_joints, -1)) * 255  # need from [0, 1] to [0, 255]
        heatmaps = F.softmax(heatmaps, dim=2)  # [0, 1]
        heatmaps = heatmaps.reshape((batch_size, num_joints, widthx, heighty)).permute(0, 2, 3, 1)

        arangex = xx.reshape((1, widthx, heighty, 1)).repeat(batch_size, 1, 1, num_joints)
        if self.cuda:
            arangex = arangex.cuda()
        x_out = heatmaps.mul(arangex).sum(dim=(1, 2))
        arangey = yy.reshape((1, widthx, heighty, 1)).repeat(batch_size, 1, 1, num_joints)
        if self.cuda:
            arangey = arangey.cuda()
        y_out = heatmaps.mul(arangey).sum(dim=(1, 2))
        coord_out = torch.cat([y_out.reshape((batch_size, num_joints, 1)), x_out.reshape((batch_size, num_joints, 1))], dim=2)
        coord_out -= 1
        # coord_out *= 4.0
        # coord_out /= torch.cuda.FloatTensor([widthx, heighty])
        return coord_out  # B*N*2, [real_x, real_y]


def func_soft_argmax(heatmaps, cuda=True):
    """
    SoftArgMax2d(x) = (\sum_i \sum_j (i * softmax2d(x)_ij), \sum_i \sum_j (j * softmax2d(x)_ij))
    """
    batch_size = heatmaps.shape[0]
    num_joints = heatmaps.shape[1]
    heighty = heatmaps.shape[2]
    widthx = heatmaps.shape[3]
    # need change x and y
    y = torch.arange(widthx)
    x = torch.arange(heighty)
    xx, yy = torch.meshgrid(x, y)
    xx = xx.float() + 1
    yy = yy.float() + 1

    # heat = heatmaps[0, -1].numpy()
    # yy_max, xx_max = np.unravel_index(heat.argmax(), heat.shape)
    # print(yy_max, xx_max, heat[yy_max][xx_max])
    heatmaps = heatmaps.reshape((batch_size, num_joints, -1)) * 255  # need from [0, 1] to [0, 255]
    heatmaps = F.softmax(heatmaps, dim=2)  # [0, 1]
    heatmaps = heatmaps.reshape((batch_size, num_joints, widthx, heighty)).permute(0, 2, 3, 1)

    arangex = xx.reshape((1, widthx, heighty, 1)).repeat(batch_size, 1, 1, num_joints)
    if cuda:
        arangex = arangex.cuda()
    x_out = heatmaps.mul(arangex).sum(dim=(1, 2))
    arangey = yy.reshape((1, widthx, heighty, 1)).repeat(batch_size, 1, 1, num_joints)
    if cuda:
        arangey = arangey.cuda()
    y_out = heatmaps.mul(arangey).sum(dim=(1, 2))
    coord_out = torch.cat([y_out.reshape((batch_size, num_joints, 1)), x_out.reshape((batch_size, num_joints, 1))], dim=2)
    coord_out -= 1
    # coord_out *= 4.0
    # coord_out /= torch.Tensor([widthx, heighty])
    return coord_out  # B*N*2, [real_x, real_y]


def render_onehot_heatmap(coord, output_shape):
    batch_size = coord.shape[0]
    num_joints = coord.shape[1]

    x = torch.reshape(coord[:, :, 0], (-1, ))  # [ZL] note order
    y = torch.reshape(coord[:, :, 1], (-1, ))
    x_floor = torch.floor(x)
    y_floor = torch.floor(y)

    x_floor = x_floor.clamp(0, output_shape[0] - 2)  # fix out-of-bounds x
    y_floor = y_floor.clamp(0, output_shape[1] - 2)  # fix out-of-bounds y

    tmp = torch.arange(batch_size).cuda().unsqueeze(dim=0)  # [32] => [1, 32]
    tmp = tmp.repeat(num_joints, 1).permute(1, 0)  # [17, 32] => [32, 17]
    indices_batch = tmp.reshape((-1, )).unsqueeze(dim=1).type(torch.float32)  # [544] => [544, 1]
    indices_batch = torch.cat([indices_batch, indices_batch, indices_batch, indices_batch], dim=0)
    indices_joint = torch.arange(num_joints).cuda().repeat(batch_size).unsqueeze(dim=1).type(torch.float32)
    indices_joint = torch.cat([indices_joint, indices_joint, indices_joint, indices_joint], dim=0)

    indices_lt = torch.cat([y_floor.unsqueeze(1), x_floor.unsqueeze(1)], dim=1)
    indices_lb = torch.cat([(y_floor + 1).unsqueeze(1), x_floor.unsqueeze(1)], dim=1)
    indices_rt = torch.cat([y_floor.unsqueeze(1), (x_floor + 1).unsqueeze(1)], dim=1)
    indices_rb = torch.cat([(y_floor + 1).unsqueeze(1), (x_floor + 1).unsqueeze(1)], dim=1)

    indices = torch.cat([indices_lt, indices_lb, indices_rt, indices_rb], dim=0).type(torch.float32)  # type:torch.Tensor
    indices = torch.cat([indices_batch, indices_joint, indices], dim=1).type(torch.int64)  # [ZL] order: same to heatmap

    prob_lt = (1 - (x - x_floor)) * (1 - (y - y_floor))
    prob_lb = (1 - (x - x_floor)) * (y - y_floor)
    prob_rt = (x - x_floor) * (1 - (y - y_floor))
    prob_rb = (x - x_floor) * (y - y_floor)
    probs = torch.cat([prob_lt, prob_lb, prob_rt, prob_rb], dim=0)

    # heatmap = tf.scatter_nd(indices, probs, (batch_size, *cfg.output_shape, cfg.num_joints))
    heatmap = torch.zeros((batch_size, num_joints, *output_shape), dtype=torch.float32).cuda()
    heatmap[indices[:, 0], indices[:, 1], indices[:, 3], indices[:, 2]] = probs  # no accumulating, compared to scatter_nd
    normalizer = heatmap.sum(dim=(2, 3)).reshape((batch_size, num_joints, 1, 1))
    normalizer = torch.where(torch.eq(normalizer, 0.), torch.ones_like(normalizer), normalizer)
    heatmap = heatmap / normalizer

    return heatmap
