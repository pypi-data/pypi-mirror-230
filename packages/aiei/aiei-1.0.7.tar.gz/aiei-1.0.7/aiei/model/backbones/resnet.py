"""
(c) ZL-2020.
@author ZhaoLei
@since 2020.06.24 13:28
"""
import math
import torch.nn as nn
import torch
from torchvision.models import resnet
from collections import OrderedDict
from torchvision import ops as tv_ops
from aiei.core.base_config import cfg
from aiei.model.layers import norm
from aiei.misc import mix, summary

__all__ = ['ResNet', 'FPN', 'ResNetDCN']


class CFG():  # CFG can also be changed by kwargs
    MODEL_DIR = f'{cfg.AIEI.TORCH_MODEL_HOME}/resnet'

    class RESNET():
        NORM = norm.get_norm()


class ResNet(nn.Module):
    """
    Args:
        resnet_type (str, optional): resnet_type. Defaults to 'resnet18'.
        pretrained (bool, optional): pretrained. Defaults to True.
        kwargs:
            norm_layer ([type], optional): e.g.: norm.FrozenBatchNorm2d. Defaults to None.
    """
    def __init__(self, resnet_type='resnet18', pretrained=True, **kwargs):
        super().__init__()
        if 'norm_layer' in kwargs:
            CFG.RESNET.NORM = kwargs['norm_layer']
        assert resnet_type in resnet.__all__, f'resnet_type={resnet_type} not in support list {resnet.__all__}.'
        # backbone = resnet.resnet50(pretrained=False)
        backbone = eval(f'resnet.{resnet_type}')(pretrained=False, norm_layer=CFG.RESNET.NORM)
        if pretrained:
            backbone = mix.load_state_dict_from_url(backbone, resnet.model_urls[resnet_type], CFG.MODEL_DIR, resnet_type)
        self.stage0 = nn.Sequential(backbone.conv1, backbone.bn1, backbone.relu, backbone.maxpool)
        self.stage1 = backbone.layer1
        self.stage2 = backbone.layer2
        self.stage3 = backbone.layer3
        self.stage4 = backbone.layer4

    def forward(self, x):
        x = self.stage0(x)
        x1 = self.stage1(x)
        x2 = self.stage2(x1)
        x3 = self.stage3(x2)
        x4 = self.stage4(x3)
        return [x1, x2, x3, x4]


# FPN (for flexibility, you'd better use FeaturePyramidNetwork directly in your net)
class FPN(nn.Module):
    def __init__(self, resnet_depth=50, pretrained=True, **kwargs):
        super().__init__()
        self.res = ResNet(f'resnet{resnet_depth}', pretrained=pretrained, **kwargs)
        self.fpn = tv_ops.FeaturePyramidNetwork([256, 512, 1024, 2048] if resnet_depth >= 50 else [64, 128, 256, 512],
            256 if resnet_depth >= 50 else 64)

    def forward(self, x):
        x1, x2, x3, x4 = self.res(x)
        ipt = OrderedDict({'feat1': x1, 'feat2': x2, 'feat3': x3, 'feat4': x4})
        result = self.fpn(ipt)  # type: dict
        return [v for v in result.values()]  # high resolution is first


# ResNetDCN
class DeconvLayer(nn.Module):
    def __init__(self, in_planes, out_planes, deconv_kernel, deconv_stride=2, deconv_pad=1, deconv_out_pad=0):
        super(DeconvLayer, self).__init__()
        # from ops.FAIR.deform_conv_with_off import DeformConvWithOff, ModulatedDeformConvWithOff

        de_groups, dk_size = 1, 3
        self.offset = nn.Conv2d(in_planes, de_groups * 3 * dk_size * dk_size, kernel_size=dk_size, stride=1, padding=1)
        self.dcn = tv_ops.DeformConv2d(in_planes, out_planes, kernel_size=3, stride=1, padding=1, groups=de_groups)
        self.dcn_bn = nn.BatchNorm2d(out_planes)
        self.up_sample = nn.ConvTranspose2d(out_planes, out_planes, kernel_size=deconv_kernel, stride=deconv_stride,
            padding=deconv_pad, output_padding=deconv_out_pad, bias=False)
        # self.up_sample = nn.UpsamplingBilinear2d(scale_factor=2)
        self._deconv_init()
        self.up_bn = nn.BatchNorm2d(out_planes)
        self.relu = nn.ReLU()

    def forward(self, x):
        off = self.offset(x)
        o1, o2, mask = torch.chunk(off, 3, dim=1)
        offset = torch.cat((o1, o2), dim=1)
        mask = torch.sigmoid(mask)
        x = self.dcn(x, offset, mask)
        x = self.dcn_bn(x)
        x = self.relu(x)
        x = self.up_sample(x)
        x = self.up_bn(x)
        x = self.relu(x)
        return x

    def _deconv_init(self):
        w = self.up_sample.weight.data
        f = math.ceil(w.size(2) / 2)
        c = (2 * f - 1 - f % 2) / (2. * f)
        for i in range(w.size(2)):
            for j in range(w.size(3)):
                w[0, 0, i, j] = (1 - math.fabs(i / f - c)) * (1 - math.fabs(j / f - c))
        for c in range(1, w.size(0)):
            w[c, 0, :, :] = w[0, 0, :, :]


class DeconvUp(nn.Module):
    def __init__(self):
        super(DeconvUp, self).__init__()
        channels = [512, 256, 128, 64]
        deconv_kernel = [4, 4, 4]
        self.deconv1 = DeconvLayer(channels[0], channels[1], deconv_kernel=deconv_kernel[0])
        self.deconv2 = DeconvLayer(channels[1], channels[2], deconv_kernel=deconv_kernel[1])
        self.deconv3 = DeconvLayer(channels[2], channels[3], deconv_kernel=deconv_kernel[2])

    def forward(self, x):
        x = self.deconv1(x)
        x = self.deconv2(x)
        x = self.deconv3(x)
        return x


class ResNetDCN(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = ResNet()
        self.upsample = DeconvUp()

    def forward(self, inputs):
        x = self.backbone(inputs)[-1]
        x = self.upsample(x)
        return x


def smooth(in_cs, out_cs):
    return nn.Sequential(
        nn.Conv2d(in_cs, out_cs, kernel_size=3, stride=1, padding=1, bias=False),
        nn.BatchNorm2d(out_cs),
        nn.ReLU(inplace=True),
    )


class ResNetDCNShortcut(nn.Module):
    def __init__(self, net_type='resnet18'):
        super().__init__()
        self.backbone = ResNet(resnet_type=net_type)
        channels = [512, 256, 128, 64]
        deconv_kernel = [4, 4, 4]
        modulate_deform = True
        self.deconv1 = DeconvLayer(channels[0], channels[1], deconv_kernel=deconv_kernel[0], modulate_deform=modulate_deform)
        self.deconv2 = DeconvLayer(channels[1], channels[2], deconv_kernel=deconv_kernel[1], modulate_deform=modulate_deform)
        self.deconv3 = DeconvLayer(channels[2], channels[3], deconv_kernel=deconv_kernel[2], modulate_deform=modulate_deform)

        self.shortcut1 = nn.Sequential(
            nn.Conv2d(channels[-1], channels[-1], kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels[-1], channels[-1], kernel_size=3, stride=1, padding=1),
        )
        self.shortcut2 = nn.Sequential(
            nn.Conv2d(channels[-2], channels[-2], kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels[-2], channels[-2], kernel_size=3, stride=1, padding=1),
        )
        self.shortcut3 = nn.Sequential(nn.Conv2d(channels[-3], channels[-3], kernel_size=3, stride=1, padding=1), )
        self.smooth1 = smooth(channels[-1], channels[-1])
        self.smooth2 = smooth(channels[-2], channels[-2])
        self.smooth3 = smooth(channels[-3], channels[-3])

    def forward(self, inputs):
        x1, x2, x3, x4 = self.backbone(inputs)
        sx1 = self.shortcut1(x1)
        sx2 = self.shortcut2(x2)
        sx3 = self.shortcut3(x3)
        x3 = self.smooth3(self.deconv1(x4) + sx3)
        x2 = self.smooth2(self.deconv2(x3) + sx2)
        x1 = self.smooth1(self.deconv3(x2) + sx1)
        return x1


if __name__ == '__main__':
    import os

    os.environ['CUDA_VISIBLE_DEVICES'] = '3'
    t_net = FPN(50, norm_layer=norm.get_norm('FrozenBN'))
    # CFG.RESNET.NORM = norm.get_norm('FrozenBN')
    # t_net = FPN(50)
    # t_net = ResNetDCN()
    print(t_net, f'\nTotal params: {mix.get_num_params(t_net)}MB')
    # summary.summary(net, torch.ones(2, 3, 192, 256))
    summary.summary2(t_net.cuda(), torch.ones(2, 3, 512, 512).cuda())
    # summary.summary3(net, (torch.ones(2, 3, *cfg.input_shape),))
