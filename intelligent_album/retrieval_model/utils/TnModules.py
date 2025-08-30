import torch
import torch.nn as nn


def Ternarize(W):
    with torch.no_grad():
        m = W.abs().mean()

        m *= 2
        W = torch.clamp(torch.round(W / m), min=-1, max=1)

        return W * m

def geometric_Ternarize(W):
    with torch.no_grad():
        # 计算几何均值
        m = torch.exp(torch.mean(torch.log(W.abs() + 1e-8)))  # 防止对 0 取对数，加上一个小的偏移量
        m *= 4  # 你原始代码中对均值的操作
        W = torch.clamp(torch.round(W / m), min=-1, max=1)  # 将权重进行二值化
        return W* m

def harmonic_Ternarize(W):
    with torch.no_grad():
        # 计算调和均值
        m = W.abs().reciprocal().mean().reciprocal()  # 调和均值
        m *= 2  # 你原始代码中对均值的操作
        W = torch.clamp(torch.round(W / m), min=-1, max=1)  # 将权重进行二值化
        return W, m

class TnLinear(nn.Linear):
    def __init__(self, *args, **kwargs):
        super(TnLinear, self).__init__(*args, **kwargs)

    def forward(self, x):
        w = self.weight
        w_tn = w + (Ternarize(w.data)- w).detach()

        output = nn.functional.linear(x, w_tn, self.bias)
        return output


def replace_linear(model):
    for name, module in model.named_children():
        if isinstance(module, nn.Linear):
            # print(f"Replacing {name} with TnLinear")
            new_linear = TnLinear(
                in_features=module.in_features,
                out_features=module.out_features,
                bias=(module.bias is not None)
            )
            new_linear.weight = module.weight
            if module.bias is not None:
                new_linear.bias = module.bias

            #new_layers = new_linear
            setattr(model, name, new_linear)
        elif len(list(module.children())) > 0:
            replace_linear(module)