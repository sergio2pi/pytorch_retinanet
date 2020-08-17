from typing import Callable

import torch
import torch.nn as nn
import torchvision

__all__ = ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152']

funcs = {
    'resnet18': torchvision.models.resnet18,
    'resnet34': torchvision.models.resnet34,
    'resnet50': torchvision.models.resnet50,
    'resnet101': torchvision.models.resnet101,
    'resnet152': torchvision.models.resnet152,
}


class EmptyLayer(nn.Module):
    """PlaceHolder for AvgPool and FC Layer"""

    def __init__(self) -> None:
        super(EmptyLayer, self).__init__()

    def forward(self, xb):
        return xb


# Dictionary to store Intermediate Outputs
inter_outs = {}


class BackBone(nn.Module):
    def __init__(self, kind: str = 'resnet18', hook_fn: Callable = None, pretrained: bool = True) -> None:
        """Create a Backbone from `kind`"""
        super(BackBone, self).__init__()
        build_fn = funcs[kind]
        self.backbone = build_fn(pretrained=pretrained)
        self.backbone.avgpool = EmptyLayer()
        self.backbone.fc = EmptyLayer()

        # Get the Feature maps from the intermediate layer outputs
        self.backbone.layer2.register_forward_hook(hook_fn)
        self.backbone.layer3.register_forward_hook(hook_fn)
        self.backbone.layer4.register_forward_hook(hook_fn)

    def forward(self, xb):
        _ = self.backbone(xb)
        out = [inter_outs[self.backbone.layer2],
               inter_outs[self.backbone.layer3], inter_outs[self.backbone.layer4]]
        return out


def get_backbone(kind: str = 'resnet18', pretrained: bool = True) -> nn.Module:
    """
    Returns a `ResNet` Backbone.

    Args:
        1. kind       : (str) name of the resnet model eg: `resnet18`.
        2. pretrained : (bool) wether to load pretrained weights.

    Example:
        >>> m = get_backbone(kind='resnet18')
    """
    assert kind in __all__, f"`kind` must be one of {__all__} got {kind}"

    def hook_outputs(self, inp, out) -> None:
        # Function to Hook Intermediate Outputs
        inter_outs[self] = out

    backbone = BackBone(kind=kind, hook_fn=hook_outputs, pretrained=pretrained)

    return backbone


# if __name__ == '__main__':
#     m = get_backbone(kind='resnet18')
#     outs = m(torch.zeros(1, 3, 600, 600))
#     print('Resnet18 outputs', [o.shape for o in outs])
#     print()

#     m = get_backbone(kind='resnet34')
#     outs = m(torch.zeros(1, 3, 600, 600))
#     print('Resnet34 outputs', [o.shape for o in outs])
#     print()

#     m = get_backbone(kind='resnet50')
#     outs = m(torch.zeros(1, 3, 600, 600))
#     print('Resnet50 outputs', [o.shape for o in outs])
#     print()

#     m = get_backbone(kind='resnet101')
#     outs = m(torch.zeros(1, 3, 600, 600))
#     print('Resnet101 outputs', [o.shape for o in outs])
#     print()

#     m = get_backbone(kind='resnet152')
#     outs = m(torch.zeros(1, 3, 600, 600))
#     print('Resnet152 outputs', [o.shape for o in outs])
#     print()

    # m1 = get_backbone(kind='resnet50')
    # m2 = get_backbone(kind='resnet18')
    # m3 = get_backbone(kind='resnet101')
    # # print(m1.backbone.layer2[2].conv3.out_channels)
    # # print(m2.backbone.layer2[1].conv2.out_channels)
    # print(m2)
    # print("=="*100)
    # print(m1)
    # print("=="*100)
    # print(m3)
