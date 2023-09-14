from torch import nn
import torch

from aiei.misc import summary

NUM_JOINTS = 17
Pool = nn.MaxPool2d


class Merge(nn.Module):
    def __init__(self, x_dim, y_dim):
        super(Merge, self).__init__()
        self.conv = Conv(x_dim, y_dim, 1, relu=False, bn=False)

    def forward(self, x):
        return self.conv(x)


def batchnorm(x):
    return nn.BatchNorm2d(x.size()[1])(x)


def weights_init(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        n = m.kernel_size[0] * m.kernel_size[1] * m.in_channels
        m.weight.data.normal_(0, (1. / n) ** 0.5)


class Full(nn.Module):
    def __init__(self, inp_dim, out_dim, bn=False, relu=False):
        super(Full, self).__init__()
        self.fc = nn.Linear(inp_dim, out_dim, bias=True)
        self.relu = None
        self.bn = None
        if relu:
            self.relu = nn.ReLU()
        if bn:
            self.bn = nn.BatchNorm2d(out_dim)

    def forward(self, x):
        x = self.fc(x.view(x.size()[0], -1))
        if self.relu is not None:
            x = self.relu(x)
        if self.bn is not None:
            x = self.bn(x)
        return x


class Conv(nn.Module):
    def __init__(self, inp_dim, out_dim, kernel_size=3, stride=1, bn=False, relu=True):
        super(Conv, self).__init__()
        self.inp_dim = inp_dim
        self.conv = nn.Conv2d(inp_dim, out_dim, kernel_size, stride, padding=(kernel_size - 1) // 2, bias=True)
        self.relu = None
        self.bn = None
        if relu:
            self.relu = nn.ReLU()
        if bn:
            self.bn = nn.BatchNorm2d(out_dim)

    def forward(self, x):
        assert x.size()[1] == self.inp_dim, "{} {}".format(x.size()[1], self.inp_dim)
        x = self.conv(x)
        if self.relu is not None:
            x = self.relu(x)
        if self.bn is not None:
            x = self.bn(x)
        return x


class Hourglass(nn.Module):
    def __init__(self, n, f, bn=None, increase=128):
        super(Hourglass, self).__init__()
        nf = f + increase
        self.up1 = Conv(f, f, 3, bn=bn)
        # Lower branch
        self.pool1 = Pool(2, 2)
        self.low1 = Conv(f, nf, 3, bn=bn)
        # Recursive hourglass
        if n > 1:
            self.low2 = Hourglass(n - 1, nf, bn=bn)
        else:
            self.low2 = Conv(nf, nf, 3, bn=bn)
        self.low3 = Conv(nf, f, 3)
        self.up2 = nn.UpsamplingNearest2d(scale_factor=2)

    def forward(self, x):
        up1 = self.up1(x)
        pool1 = self.pool1(x)
        low1 = self.low1(pool1)
        low2 = self.low2(low1)
        low3 = self.low3(low2)
        up2 = self.up2(low3)
        return up1 + up2


def deconv(in_cs, out_cs):
    return nn.Sequential(
        nn.ConvTranspose2d(in_cs, out_cs, kernel_size=4, stride=2, padding=1, output_padding=0, bias=False),
        nn.BatchNorm2d(out_cs),
        nn.ReLU(inplace=True),
    )


def conv3x3(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False)


def conv1x1(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=stride, bias=False)


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, need_down=False):
        super(BasicBlock, self).__init__()
        self.need_down = need_down
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        if need_down:
            self.downsample = nn.Sequential(
                nn.Conv2d(inplanes, planes * self.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * self.expansion),
            )
        self.stride = stride

    def forward(self, x):
        identity = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        if self.need_down:
            identity = self.downsample(x)
        out += identity
        out = self.relu(out)
        return out


class Net(nn.Module):
    def __init__(self, nstack, inp_dim, oup_dim, bn=False, increase=128, **kwargs):
        super(Net, self).__init__()
        self.pre = nn.Sequential(
            Conv(3, 64, 7, 2, bn=bn),
            Conv(64, 128, bn=bn),
            Pool(2, 2),
            Conv(128, 128, bn=bn),
            Conv(128, inp_dim, bn=bn)
        )
        self.features = nn.ModuleList([
            nn.Sequential(
                Hourglass(4, inp_dim, bn, increase),
                Conv(inp_dim, inp_dim, 3, bn=False),
                Conv(inp_dim, inp_dim, 3, bn=False)
            ) for i in range(nstack)])

        # ch = 32
        # self.deconv = deconv(256 + 2 * NUM_JOINTS, ch)
        # self.layer1_2 = nn.Sequential(
        #     BasicBlock(ch, ch),
        #     BasicBlock(ch, ch),
        #     BasicBlock(ch, ch),
        #     BasicBlock(ch, ch),
        # )

        self.outs = nn.ModuleList([Conv(inp_dim, oup_dim, 1, relu=False, bn=False) for i in range(nstack)])
        self.merge_features = nn.ModuleList([Merge(inp_dim, inp_dim) for i in range(nstack - 1)])
        self.merge_preds = nn.ModuleList([Merge(oup_dim, inp_dim) for i in range(nstack - 1)])

        # self.outs.append(nn.Conv2d(in_channels=ch, out_channels=NUM_JOINTS, kernel_size=1, stride=1, padding=0))
        # for tmp_layer in self.outs:
        #     for m in tmp_layer.modules():  # [ZL] important
        #         if isinstance(m, nn.Conv2d):
        #             # nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')  # NOT
        #             nn.init.normal_(m.weight, std=0.001)
        #             if m.bias is not None:
        #                 nn.init.constant_(m.bias, 0)

        self.nstack = nstack

    def forward(self, imgs):
        x = self.pre(imgs)
        preds = []
        for i in range(self.nstack):
            feature = self.features[i](x)
            preds.append(self.outs[i](feature))
            if i != self.nstack - 1:
                x = x + self.merge_preds[i](preds[-1]) + self.merge_features[i](feature)

        # x = torch.cat([x, preds[-1]], dim=1)
        # x = self.deconv(x)
        # x = self.layer1_2(x)
        # x = self.outs[-1](x)
        # preds.append(x)
        return preds


if __name__ == '__main__':
    net = Net(1, 256, 17, True)
    # net = TestConv()
    # summary.summary(net, torch.ones(2, 3, 192, 256))
    print(f'Total params: {sum(p.numel() for p in net.parameters()) / (1024 * 1024):.2f}MB')
    summary.summary2(net, torch.ones(2, 3, 192, 256))
    # summary.summary3(net, (torch.ones(2, 3, *cfg.input_shape),))
