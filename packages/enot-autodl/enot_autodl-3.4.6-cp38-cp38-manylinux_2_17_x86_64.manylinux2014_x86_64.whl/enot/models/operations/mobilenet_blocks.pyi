from _typeshed import Incomplete
from torch import nn
from typing import Optional

class SearchableMobileInvertedBottleneck(nn.Module):
    in_channels: Incomplete
    out_channels: Incomplete
    kernel_size: Incomplete
    stride: Incomplete
    expand_ratio: Incomplete
    padding: Incomplete
    dw_channels: Incomplete
    affine: Incomplete
    track: Incomplete
    activation_function_name: Incomplete
    activation_function: Incomplete
    expand_op: Incomplete
    depthwise_op: Incomplete
    squeeze_op: Incomplete
    use_skip_connection: Incomplete
    def __init__(self, in_channels: int, out_channels: int, dw_channels: Optional[int] = ..., expand_ratio: Optional[float] = ..., kernel_size: int = ..., stride: int = ..., padding: Optional[int] = ..., affine: bool = ..., track: bool = ..., activation: Optional[str] = ..., use_skip_connection: bool = ...) -> None: ...
    def forward(self, x): ...
