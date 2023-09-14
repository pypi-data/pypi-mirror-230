import torch.nn as nn
import torch
import math
import torch.nn.functional as F


class GAU(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(GAU, self).__init__()
        self.lateral = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
        self.seq_guide = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(out_channels, out_channels, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.Sigmoid()
        )
        # self.seq_up = nn.Sequential(
        #     nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),
        #     nn.Conv2d(256, 256, kernel_size=1, stride=1, bias=False),
        #     nn.BatchNorm2d(256)
        # )
        self.seq_up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)

    def forward(self, inputs_guide, inputs_lateral):
        tmp_inputs_lateral = inputs_lateral
        # h, w = inputs_low.size(2), inputs_low.size(3)
        inputs_guide_upsample = self.seq_up(inputs_guide)
        inputs_lateral = self.lateral(inputs_lateral)
        inputs_guide = self.seq_guide(inputs_guide)
        inputs_mul = torch.mul(inputs_lateral, inputs_guide)
        return inputs_guide_upsample + inputs_mul + self.lateral(tmp_inputs_lateral)


class GAD(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(GAD, self).__init__()
        self.lateral = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
        self.seq_guide = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(out_channels, out_channels, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.Sigmoid()
        )
        self.seq_down = nn.Sequential(
            nn.Conv2d(256, 256, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True)
        )
        # self.seq_down = nn.Upsample(scale_factor=0.5, mode='bilinear', align_corners=True)

    def forward(self, inputs_guide, inputs_lateral):
        tmp_inputs_lateral = inputs_lateral
        inputs_guide_down = self.seq_down(inputs_guide)
        inputs_lateral = self.lateral(inputs_lateral)
        inputs_guide = self.seq_guide(inputs_guide)
        inputs_mul = torch.mul(inputs_lateral, inputs_guide)
        return inputs_guide_down + inputs_mul + self.lateral(tmp_inputs_lateral)


class FPA(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(FPA, self).__init__()
        # global pooling
        self.seq_global_pooling = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

        self.seq_mid = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

        self.seq_down1 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(in_channels, 1, kernel_size=7, stride=1, padding=3, bias=False),
            nn.BatchNorm2d(1),
            nn.ReLU(inplace=True)
        )

        self.seq_down2 = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(1, 1, kernel_size=5, stride=1, padding=2, bias=False),
            nn.BatchNorm2d(1),
            nn.ReLU(inplace=True)
        )

        # self.seq_down3 = nn.Sequential(
        #     nn.MaxPool2d(kernel_size=2, stride=2),
        #     nn.Conv2d(1, 1, kernel_size=3, stride=1, padding=1),
        #     nn.BatchNorm2d(1),
        #     nn.ReLU(inplace=True),
        #     nn.Conv2d(1, 1, kernel_size=3, stride=1, padding=1),
        #     nn.BatchNorm2d(1),
        #     nn.ReLU(inplace=True)
        # )

        self.seq_conv1 = nn.Sequential(
            nn.Conv2d(1, 1, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm2d(1),
            nn.ReLU(inplace=True)
        )

        self.seq_conv2 = nn.Sequential(
            nn.Conv2d(1, 1, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(1),
            nn.ReLU(inplace=True)
        )

    def forward(self, inputs):
        h, w = inputs.size(2), inputs.size(3)
        b1 = self.seq_global_pooling(inputs)
        b1 = nn.Upsample(size=(h, w), mode='bilinear', align_corners=True)(b1)
        mid = self.seq_mid(inputs)
        x1 = self.seq_down1(inputs)
        x2 = self.seq_down2(x1)

        x1 = self.seq_conv1(x1)
        x2 = self.seq_conv2(x2)
        x2 = nn.Upsample(size=(h // 2, w // 2), mode='bilinear', align_corners=True)(x2)
        x = x2 + x1
        x = nn.Upsample(size=(h, w), mode='bilinear', align_corners=True)(x)

        x = torch.mul(x, mid)
        x = x + b1 + mid
        return x


if __name__ == '__main__':
    net = GAU(1024, 256)
    # net = FPANet(2048, 256)
    # print(net)
    print('Total params: %.2fMB' % (sum(p.numel() for p in net.parameters()) / (1024 * 1024) * 4))
