import torch.nn as nn
import torch


class HSwish(nn.Module):
    def __init__(self):
        super(HSwish, self).__init__()
        # self.relu6 = nn.ReLU6(inplace=True)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # return x * (self.relu6(x + 3) / 6) # Hard Swish
        return x * self.sigmoid(x)


class SwishFunc(torch.autograd.Function):
    @staticmethod
    def forward(ctx, i):
        result = i * torch.sigmoid(i)
        ctx.save_for_backward(i)
        return result

    @staticmethod
    def backward(ctx, grad_output):
        i = ctx.saved_variables[0]
        sigmoid_i = torch.sigmoid(i)
        return grad_output * (sigmoid_i * (1 + i * (1 - sigmoid_i)))


# less memory usage (30%)
class Swish(nn.Module):
    def forward(self, x):
        return SwishFunc.apply(x)
