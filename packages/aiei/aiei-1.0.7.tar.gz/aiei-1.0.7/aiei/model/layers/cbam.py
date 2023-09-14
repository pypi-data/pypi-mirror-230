import torch.nn as nn
import torch
import math
import torch.nn.functional as F


class CBAM(nn.Module):
    def __init__(self, channels, reduction=4):
        super(CBAM, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.fc1 = nn.Conv2d(channels, channels // reduction, kernel_size=1, padding=0)
        self.relu = nn.ReLU(inplace=True)
        self.fc2 = nn.Conv2d(channels // reduction, channels, kernel_size=1, padding=0)
        self.sigmoid_channel = nn.Sigmoid()
        self.conv_after_concat = nn.Conv2d(2, 1, kernel_size=3, stride=1, padding=1)
        self.sigmoid_spatial = nn.Sigmoid()

    def forward(self, x):
        module_input = x
        avg = self.avg_pool(x)
        mx = self.max_pool(x)
        avg = self.fc1(avg)
        mx = self.fc1(mx)
        avg = self.relu(avg)
        mx = self.relu(mx)
        avg = self.fc2(avg)
        mx = self.fc2(mx)
        x = avg + mx
        x = self.sigmoid_channel(x)
        x = module_input * x
        module_input = x
        avg = torch.mean(x, 1, True)
        mx, _ = torch.max(x, 1, True)
        x = torch.cat((avg, mx), 1)
        x = self.conv_after_concat(x)
        x = self.sigmoid_spatial(x)
        x = module_input * x
        return x


class CBAMLateral(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(CBAMLateral, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels=out_channels, kernel_size=1, stride=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
        self.cbam = CBAM(out_channels, reduction=8)

    def forward(self, inputs):
        out1 = self.conv(inputs)
        out2 = self.cbam(out1)
        out = out1 + out2
        return out


if __name__ == '__main__':
    net = CBAMLateral(2048, 256)
    # print(net)
    print('Total params: %.2fMB' % (sum(p.numel() for p in net.parameters()) / (1024 * 1024) * 4))
