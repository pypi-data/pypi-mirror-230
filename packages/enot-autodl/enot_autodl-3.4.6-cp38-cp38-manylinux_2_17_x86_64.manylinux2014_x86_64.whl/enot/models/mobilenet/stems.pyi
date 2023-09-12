from _typeshed import Incomplete
from torch import nn
from typing import Optional, Tuple

class MobileNetBaseStem(nn.Module):
    width_multiplier: Incomplete
    in_channels: Incomplete
    min_channels: Incomplete
    stem: Incomplete
    def __init__(self, *, activation: Optional[str] = ..., in_channels: int = ..., strides: Tuple[int, int] = ..., output_channels: Tuple[int, int] = ..., kernel_sizes: Tuple[int, int] = ..., width_multiplier: float = ..., min_channels: int = ...) -> None: ...
    def forward(self, x): ...

MobileNetCifarStem: Incomplete
