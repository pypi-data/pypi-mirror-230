import torch
from _typeshed import Incomplete
from torch import nn

class MobileNetBaseHead(nn.Module):
    last_channels: Incomplete
    bottleneck_channels: Incomplete
    width_multiplier: Incomplete
    num_classes: Incomplete
    head: Incomplete
    def __init__(self, bottleneck_channels: int, *, activation: str = ..., last_channels: int = ..., dropout_rate: float = ..., num_classes: int = ..., width_multiplier: float = ...) -> None: ...
    def forward(self, x): ...

class ArcfaceHead(nn.Linear):
    radius: Incomplete
    angle_margin: Incomplete
    cos_margin: Incomplete
    angle_scale: Incomplete
    num_classes: Incomplete
    vectorizer: Incomplete
    def __init__(self, bottleneck_channels: int, *, radius: float = ..., angle_margin: float = ..., cos_margin: float = ..., angle_scale: float = ..., last_channels: int = ..., num_classes: int = ...) -> None: ...
    def forward(self, inputs: torch.Tensor, labels: torch.Tensor = ...) -> torch.Tensor: ...
    @staticmethod
    def corrected_cos(inputs: torch.Tensor) -> torch.Tensor: ...
