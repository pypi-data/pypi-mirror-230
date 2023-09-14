import torch.nn as nn
import torch
import torch.nn.functional as F


class HSwish(nn.Module):
    def __init__(self):
        super(HSwish, self).__init__()
        # self.relu6 = nn.ReLU6(inplace=True)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # return x * (self.relu6(x + 3) / 6)
        return x * self.sigmoid(x)


def add_coord(feat):
    x_range = torch.linspace(-1, 1, feat.shape[-1], device=feat.device)
    y_range = torch.linspace(-1, 1, feat.shape[-2], device=feat.device)
    y, x = torch.meshgrid(y_range, x_range)
    y = y.expand([feat.shape[0], 1, -1, -1])
    x = x.expand([feat.shape[0], 1, -1, -1])
    coord_feat = torch.cat([x, y], 1)
    feat = torch.cat([feat, coord_feat], 1)
    return feat


def deconv(in_cs, out_cs):
    return nn.Sequential(
        nn.ConvTranspose2d(in_cs, out_cs, kernel_size=4, stride=2, padding=1, output_padding=0, bias=False),
        nn.BatchNorm2d(out_cs),
        nn.ReLU(inplace=True),
    )


def lateral(in_cs, out_cs):
    return nn.Sequential(
        nn.Conv2d(in_cs, out_channels=out_cs, kernel_size=1, stride=1, bias=False),
        nn.BatchNorm2d(out_cs),
        nn.ReLU(inplace=True),
    )


def smooth(in_cs, out_cs):
    # return Bottleneck(in_cs, out_cs // 4, stride=1, need_down=True)
    return nn.Sequential(
        nn.Conv2d(in_cs, out_cs, kernel_size=3, stride=1, padding=1, bias=False),
        # nn.Conv2d(in_cs, out_cs, kernel_size=(1, 3), stride=1, padding=(0, 1)),
        # nn.Conv2d(out_cs, out_cs, kernel_size=(3, 1), stride=1, padding=(1, 0)),
        nn.BatchNorm2d(out_cs),
        nn.ReLU(inplace=True),
    )


# self.bott1 = Bottleneck(1024, 512, stride=2, need_down=True)
# self.bott2 = Bottleneck(2048, 512)
# self.bott1 = Bottleneck(64, 64, stride=1, need_down=True)
class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, stride=1, need_down=False):
        super(Bottleneck, self).__init__()
        self.need_down = need_down
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, stride=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * self.expansion, kernel_size=1, stride=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * self.expansion)
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
        out = self.relu(out)
        out = self.conv3(out)
        out = self.bn3(out)
        if self.need_down:
            identity = self.downsample(x)
        out += identity
        out = self.relu(out)
        return out


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, need_down=False):
        super(BasicBlock, self).__init__()
        self.need_down = need_down
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
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


class LastOutA(nn.Module):
    def __init__(self, last_in_cs, last_out_cs):
        super(LastOutA, self).__init__()
        self.down = nn.Sequential(
            nn.Conv2d(last_in_cs, last_out_cs, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(last_out_cs),
            nn.ReLU(inplace=True),
        )

    def forward(self, last_inputs):
        return self.down(last_inputs)


class LastOutB(nn.Module):
    def __init__(self, last_in_cs, last_out_cs):
        super(LastOutB, self).__init__()
        self.shuffle = nn.PixelShuffle(2)
        self.smooth = smooth(last_in_cs // 4 + last_out_cs, last_out_cs)

    def forward(self, last_inputs_a, last_inputs_b):
        x = torch.cat([self.shuffle(last_inputs_a), last_inputs_b], dim=1)
        return self.smooth(x)


class DownLayer(nn.Module):
    def __init__(self, in_cs):
        super(DownLayer, self).__init__()
        list_layer = []
        self.inplanes = in_cs[0]
        num_blocks = [2, 2, 2]
        for i in range(1, len(in_cs)):
            list_block = [BasicBlock(in_cs[i - 1], in_cs[i] // BasicBlock.expansion, stride=2, need_down=True)]
            for _ in range(num_blocks[i - 1] - 1):
                list_block.append(BasicBlock(in_cs[i], in_cs[i] // BasicBlock.expansion))
            list_layer.append(nn.Sequential(*list_block))
            # list_layer.append(self._make_layer(Bottleneck, in_cs[0] // 2 * 2 ** (i - 1), num_blocks[i - 1], stride=2))
        self.list_layer = nn.ModuleList(list_layer)

    def forward(self, list_input):
        outs = [list_input[0]]
        for i in range(len(list_input) - 1):
            x = self.list_layer[i](outs[-1]) + list_input[i + 1]
            outs.append(x)
        return outs

    @staticmethod
    def test():
        test_net = DownLayer([32, 64, 128])
        outs = test_net([torch.ones(2, 32, 48, 64), torch.ones(2, 64, 24, 32), torch.ones(2, 128, 12, 16)])
        for out in outs:
            print(out.size())


class GAU(nn.Module):
    def __init__(self, in_cs, out_cs):
        super(GAU, self).__init__()
        self.seq_guide = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_cs, out_cs, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(out_cs),
            nn.Sigmoid()
        )

    def forward(self, inputs_guide, inputs_lateral):
        igud1 = self.seq_guide(inputs_guide)  # B*C*1*1
        mul1 = torch.mul(inputs_lateral, igud1)
        return mul1 + inputs_lateral


class UpLayer(nn.Module):
    def __init__(self, in_cs, out_cs):
        super(UpLayer, self).__init__()
        list_smooth = []
        list_gau = []
        self.last_smooth = smooth(in_cs[-1], out_cs[-1])
        for i in range(len(in_cs) - 1):
            # up_channel = in_cs[i + 1] if i == 0 else out_cs[i + 1]  # initial is from in_cs
            list_gau.append(GAU(out_cs[i + 1], out_cs[i + 1] // 4 + in_cs[i]))
            list_smooth.append(smooth(out_cs[i + 1] // 4 + in_cs[i], out_cs[i]))
        self.list_smooth = nn.ModuleList(list_smooth)
        self.list_gau = nn.ModuleList(list_gau)
        self.shuffle = nn.PixelShuffle(2)

    def forward(self, list_input):
        assert len(list_input) == len(self.list_smooth) + 1
        outs = []
        x = self.last_smooth(list_input[-1])
        outs.append(x)
        for i in range(len(list_input) - 2, -1, -1):
            x_lateral = list_input[i]
            x_up = self.shuffle(x)
            cat_cs = torch.cat([x_lateral, x_up], dim=1)
            cat_cs = self.list_gau[i](x, cat_cs)
            x = self.list_smooth[i](cat_cs)
            outs.append(x)
        return outs[::-1]


class DCM(nn.Module):
    def __init__(self, in_cs, out_cs, size):
        super(DCM, self).__init__()
        self.size = size
        self.out_cs = out_cs
        self.conv1 = nn.Conv2d(in_channels=in_cs, out_channels=out_cs, kernel_size=1, stride=1, padding=0)
        self.pool = nn.AdaptiveAvgPool2d(size)
        self.conv2 = nn.Conv2d(in_channels=in_cs, out_channels=out_cs, kernel_size=1, stride=1, padding=0)

    def forward(self, inputs):
        ipt = self.conv1(inputs)
        weight = torch.mean(self.conv2(self.pool(inputs)), dim=0, keepdim=True).permute(1, 0, 2, 3)
        x = F.conv2d(ipt, weight, stride=1, padding=(self.size - 1) // 2, groups=self.out_cs)
        return x

    @staticmethod
    def test():
        dcm = DCM(2048, 512, 3)
        x = dcm(torch.ones(2, 2048, 6, 8))
        print(x.size())


class Net1(nn.Module):
    def __init__(self):
        super(Net1, self).__init__()
        from nets import resnet
        self.res = resnet.resnet50(True)
        self.shuffle = nn.PixelShuffle(8)
        self.predict = nn.Conv2d(in_channels=2048 // 64, out_channels=17, kernel_size=1, stride=1, padding=0)
        for m in self.predict.modules():  # [ZL] important
            if isinstance(m, nn.Conv2d):
                # nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')  # NOT
                nn.init.normal_(m.weight, std=0.001)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)

    def forward(self, inputs):
        x = self.shuffle(self.res(inputs)[0])
        x = self.predict(x)
        return [x]


def add_conv(in_ch, out_ch, ksize, stride, leaky=True):
    stage = nn.Sequential()
    pad = (ksize - 1) // 2
    stage.add_module('conv', nn.Conv2d(in_channels=in_ch,
                                       out_channels=out_ch, kernel_size=ksize, stride=stride,
                                       padding=pad, bias=False))
    stage.add_module('batch_norm', nn.BatchNorm2d(out_ch))
    if leaky:
        stage.add_module('leaky', nn.LeakyReLU(0.1))
    else:
        stage.add_module('relu6', nn.ReLU6(inplace=True))
    return stage


# self.asff3 = ASFF(2)
# x_11 = self.asff3(x_3, x_2, x_1)
class ASFF(nn.Module):
    def __init__(self, level, rfb=False, vis=False):
        super(ASFF, self).__init__()
        self.level = level
        self.dim = [256, 128, 64]
        self.inter_dim = self.dim[self.level]
        if level == 0:
            self.stride_level_1 = add_conv(128, self.inter_dim, 3, 2)
            self.stride_level_2 = add_conv(64, self.inter_dim, 3, 2)
            self.expand = add_conv(self.inter_dim, 256, 3, 1)
        elif level == 1:
            self.compress_level_0 = add_conv(256, self.inter_dim, 1, 1)
            self.stride_level_2 = add_conv(64, self.inter_dim, 3, 2)
            self.expand = add_conv(self.inter_dim, 128, 3, 1)
        elif level == 2:
            self.compress_level_0 = add_conv(256, self.inter_dim, 1, 1)
            self.compress_level_1 = add_conv(128, self.inter_dim, 1, 1)
            self.expand = add_conv(self.inter_dim, 64, 3, 1)

        # compress_c = 8 if rfb else 16  # when adding rfb, we use half number of channels to save memory
        compress_c = 32

        self.weight_level_0 = add_conv(self.inter_dim, compress_c, 1, 1)
        self.weight_level_1 = add_conv(self.inter_dim, compress_c, 1, 1)
        self.weight_level_2 = add_conv(self.inter_dim, compress_c, 1, 1)

        self.weight_levels = nn.Conv2d(compress_c * 3, 3, kernel_size=1, stride=1, padding=0)
        self.vis = vis

    def forward(self, x_level_0, x_level_1, x_level_2):
        if self.level == 0:
            level_0_resized = x_level_0
            level_1_resized = self.stride_level_1(x_level_1)
            level_2_downsampled_inter = F.max_pool2d(x_level_2, 3, stride=2, padding=1)
            level_2_resized = self.stride_level_2(level_2_downsampled_inter)
        elif self.level == 1:
            level_0_compressed = self.compress_level_0(x_level_0)
            level_0_resized = F.interpolate(level_0_compressed, scale_factor=2, mode='bilinear', align_corners=False)
            level_1_resized = x_level_1
            level_2_resized = self.stride_level_2(x_level_2)
        elif self.level == 2:
            level_0_compressed = self.compress_level_0(x_level_0)
            level_0_resized = F.interpolate(level_0_compressed, scale_factor=4, mode='bilinear', align_corners=False)
            level_1_compressed = self.compress_level_1(x_level_1)
            level_1_resized = F.interpolate(level_1_compressed, scale_factor=2, mode='bilinear', align_corners=False)
            level_2_resized = x_level_2

        level_0_weight_v = self.weight_level_0(level_0_resized)
        level_1_weight_v = self.weight_level_1(level_1_resized)
        level_2_weight_v = self.weight_level_2(level_2_resized)
        levels_weight_v = torch.cat((level_0_weight_v, level_1_weight_v, level_2_weight_v), 1)
        levels_weight = self.weight_levels(levels_weight_v)
        levels_weight = F.softmax(levels_weight, dim=1)

        fused_out_reduced = level_0_resized * levels_weight[:, 0:1, :, :] + \
            level_1_resized * levels_weight[:, 1:2, :, :] + \
            level_2_resized * levels_weight[:, 2:, :, :]

        out = self.expand(fused_out_reduced)

        if self.vis:
            return out, levels_weight, fused_out_reduced.sum(dim=1)
        else:
            return out


if __name__ == '__main__':
    # import os
    # os.environ['CUDA_VISIBLE_DEVICES'] = '2'  # if u.se this, net and inputs need add .cuda()
    from misc import summary
    DCM.test()

    net = Net1()
    print(f'Total params: {sum(p.numel() for p in net.parameters()) / (1024 * 1024):.2f}MB')
    summary.summary2(net, torch.ones(2, 3, 192, 256))
    # summary.summary3(net, (torch.ones(2, 3, *cfg.input_shape),))
