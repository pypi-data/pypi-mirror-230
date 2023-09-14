import torch.nn as nn
import torch


class Swish(nn.Module):
    def __init__(self):
        super(Swish, self).__init__()
        # self.relu6 = nn.ReLU6(inplace=True)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # return x * (self.relu6(x + 3) / 6)
        return x * self.sigmoid(x)


def conv3x3(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False)


def conv1x1(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=stride, bias=False)


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
        self.conv1 = conv1x1(inplanes, planes)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = conv3x3(planes, planes, stride)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = conv1x1(planes, planes * self.expansion)
        self.bn3 = nn.BatchNorm2d(planes * self.expansion)
        self.relu = nn.ReLU(inplace=True)
        if need_down:
            self.downsample = nn.Sequential(
                conv1x1(inplanes, planes * self.expansion, stride),
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

    def __init__(self, inplanes, planes, stride=1, need_down=False, gn_group=None, use_swish=False):
        super(BasicBlock, self).__init__()
        self.need_down = need_down
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes) if gn_group is None else nn.GroupNorm(gn_group, planes)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes) if gn_group is None else nn.GroupNorm(gn_group, planes)
        self.relu = Swish() if use_swish else nn.ReLU(inplace=True)
        if need_down:
            self.downsample = nn.Sequential(
                nn.Conv2d(inplanes, planes * self.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * self.expansion) if gn_group is None else nn.GroupNorm(gn_group, planes),
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
    def __init__(self, in_cs, use_swish=False):
        super(DownLayer, self).__init__()
        list_layer = []
        self.inplanes = in_cs[0]
        num_blocks = [2, 2, 2]
        for i in range(1, len(in_cs)):
            list_block = [
                BasicBlock(in_cs[i - 1], in_cs[i] // BasicBlock.expansion, stride=2, need_down=True, use_swish=use_swish)
            ]
            for _ in range(num_blocks[i - 1] - 1):
                list_block.append(BasicBlock(in_cs[i], in_cs[i] // BasicBlock.expansion, use_swish=use_swish))
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
        self.seq_guide = nn.Sequential(nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_cs, out_cs, kernel_size=1, stride=1, padding=0, bias=False), nn.BatchNorm2d(out_cs), nn.Sigmoid())

    def forward(self, inputs_guide, inputs_lateral):
        igud1 = self.seq_guide(inputs_guide)  # B*C*1*1
        mul1 = torch.mul(inputs_lateral, igud1)
        return mul1 + inputs_lateral


class UpLayer(nn.Module):
    def __init__(self, in_cs, out_cs):
        super(UpLayer, self).__init__()
        list_smooth, list_gau, list_lat_smooth = [], [], []
        self.last_smooth = smooth(in_cs[-1], out_cs[-1])
        for i in range(len(in_cs) - 1):
            # up_channel = in_cs[i + 1] if i == 0 else out_cs[i + 1]  # initial is from in_cs
            # list_lat_smooth.append(smooth(out_cs[i + 1], out_cs[i + 1]))
            list_gau.append(GAU(out_cs[i + 1], out_cs[i + 1] // 4 + in_cs[i]))
            list_smooth.append(smooth(out_cs[i + 1] // 4 + in_cs[i], out_cs[i]))
        self.list_smooth = nn.ModuleList(list_smooth)
        self.list_gau = nn.ModuleList(list_gau)
        # self.list_lat_smooth = nn.ModuleList(list_lat_smooth)
        self.shuffle = nn.PixelShuffle(2)

    def forward(self, list_input):
        assert len(list_input) == len(self.list_smooth) + 1
        outs = []
        x = self.last_smooth(list_input[-1])
        outs.append(x)
        for i in range(len(list_input) - 2, -1, -1):
            x_lateral = list_input[i]
            # x = self.list_lat_smooth[i](x)
            x_up = self.shuffle(x)
            cat_cs = torch.cat([x_lateral, x_up], dim=1)
            cat_cs = self.list_gau[i](x, cat_cs)
            x = self.list_smooth[i](cat_cs)
            outs.append(x)
        return outs[::-1]


class BasicLx(nn.Module):
    def __init__(self, ic=64, lx=2):
        super().__init__()
        assert lx in [1, 2], 'only support lx in [1, 2]'
        self.lx = lx
        chs = [ic, 2 * ic, 4 * ic, 4 * ic]
        self.down4 = DownLayer(chs[:4])
        self.up4 = UpLayer(chs[:4], chs[:4])
        if self.lx == 2:
            self.down5 = DownLayer(chs[:4])
            self.up5 = UpLayer(chs[:4], chs[:4])

        MODEL_HOME = ''
        try:
            from aiei.core.base_config import cfg
            MODEL_HOME = f'{cfg.AIEI.TORCH_MODEL_HOME}/tnet'
        except Exception as e:
            pass
        if MODEL_HOME != '':
            state_dict = self.state_dict()
            pre_state_dict = torch.load(f"{MODEL_HOME}/TNet_D2W{chs[0]}.pth", map_location=lambda storage, loc: storage)
            count = 0
            for k, v in pre_state_dict.items():
                if k not in state_dict:
                    continue
                state_dict[k] = v
                count += 1
            print(f'BasicL{self.lx} successfully load {count} keys')
            self.load_state_dict(state_dict)

    def forward(self, x):
        assert isinstance(x, list), 'x should be list'
        x = self.down4(x)
        x = self.up4(x)
        if self.lx == 2:
            x = self.down5(x)
            x = self.up5(x)
        return x  # [x_1, x_2, x_3, x_4]


class TNetD2(nn.Module):
    def __init__(self, ic=64, dx=2):
        super().__init__()
        assert dx in [1, 2], 'only support dx in [1, 2]'
        self.dx = dx
        chs = [ic, 2 * ic, 4 * ic, 4 * ic]
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=2, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.conv2 = nn.Conv2d(64, chs[0], kernel_size=3, stride=2, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(chs[0])
        self.relu = nn.ReLU(inplace=True)
        self.layer1_1 = nn.Sequential(
            BasicBlock(chs[0], chs[0]),
            BasicBlock(chs[0], chs[0]),
            BasicBlock(chs[0], chs[0]),
            BasicBlock(chs[0], chs[0]),
        )

        self.last_out1 = LastOutA(chs[0], chs[1])
        self.down2 = DownLayer(chs[:2])
        self.up2 = UpLayer(chs[:2], chs[:2])
        self.last_out2 = LastOutA(chs[1], chs[2])
        self.down3 = DownLayer(chs[:3])
        self.up3 = UpLayer(chs[:3], chs[:3])
        self.last_out3 = LastOutA(chs[2], chs[3])
        self.down4 = DownLayer(chs[:4])
        self.up4 = UpLayer(chs[:4], chs[:4])
        if self.dx == 2:
            self.down5 = DownLayer(chs[:4])
            self.up5 = UpLayer(chs[:4], chs[:4])

        MODEL_HOME = ''
        try:
            from aiei.core.base_config import cfg
            MODEL_HOME = f'{cfg.AIEI.TORCH_MODEL_HOME}/tnet'
        except Exception as e:
            pass
        if MODEL_HOME != '':
            state_dict = self.state_dict()
            pre_state_dict = torch.load(f"{MODEL_HOME}/TNet_D{self.dx}W{chs[0]}.pth", map_location=lambda storage, loc: storage)
            count = 0
            for k, v in pre_state_dict.items():
                if k not in state_dict:
                    continue
                state_dict[k] = v
                count += 1
            print(f'TNetD{self.dx} successfully load {count} keys')
            self.load_state_dict(state_dict)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x_1 = self.relu(x)
        x_1 = self.layer1_1(x_1)

        x_1, x_2 = x_1, self.last_out1(x_1)
        x_1, x_2 = self.down2([x_1, x_2])
        x_1, x_2 = self.up2([x_1, x_2])
        x_3 = self.last_out2(x_2)
        x_1, x_2, x_3 = self.down3([x_1, x_2, x_3])
        x_1, x_2, x_3 = self.up3([x_1, x_2, x_3])
        x_4 = self.last_out3(x_3)
        x_1, x_2, x_3, x_4 = self.down4([x_1, x_2, x_3, x_4])
        x_1, x_2, x_3, x_4 = self.up4([x_1, x_2, x_3, x_4])
        if self.dx == 2:
            x_1, x_2, x_3, x_4 = self.down5([x_1, x_2, x_3, x_4])
            x_1, x_2, x_3, x_4 = self.up5([x_1, x_2, x_3, x_4])
        return [x_1, x_2, x_3, x_4]


class TNetD1(nn.Module):  # 1
    def __init__(self, ic=64):
        super().__init__()
        self.base1 = TNetD2(ic, dx=1)

    def forward(self, x):
        x = self.base1(x)
        return x


class TNetD3(nn.Module):  # 2+1
    def __init__(self, ic=64):
        super().__init__()
        self.base1 = TNetD2(ic)
        self.base2 = BasicLx(ic, lx=1)

    def forward(self, x):
        x = self.base1(x)
        x = self.base2(x)
        return x


class TNetD4(nn.Module):  # 2+2
    def __init__(self, ic=64):
        super().__init__()
        self.base1 = TNetD2(ic)
        self.base2 = BasicLx(ic, lx=2)

    def forward(self, x):
        x = self.base1(x)
        x = self.base2(x)
        return x


class TNetD5(nn.Module):  # 2+2+1
    def __init__(self, ic=64):
        super().__init__()
        self.base1 = TNetD2(ic)
        self.base2 = BasicLx(ic, lx=2)
        self.base3 = BasicLx(ic, lx=1)

    def forward(self, x):
        x = self.base1(x)
        x = self.base2(x)
        x = self.base3(x)
        return x


if __name__ == '__main__':
    from misc import summary

    net = TNetD2(64)
    # summary.summary(net, torch.ones(2, 3, 192, 256))
    print(f'Total params: {sum(p.numel() for p in net.parameters()) / (1024 * 1024):.2f}MB')
    summary.summary2(net, torch.ones(2, 3, 192, 256))
    # summary.summary3(net, (torch.ones(2, 3, *cfg.input_shape),))
