from _typeshed import Incomplete
from torch import nn
from typing import Optional, Tuple, Union

class SearchableConv2d(nn.Module):
    in_channels: Incomplete
    out_channels: Incomplete
    stride: Incomplete
    kernel_size: Incomplete
    padding: Incomplete
    conv2d: Incomplete
    activation_function: Incomplete
    batch_norm: Incomplete
    use_skip_connection: Incomplete
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = ..., stride: Union[int, Tuple[int, int]] = ..., padding: Optional[int] = ..., activation: Optional[str] = ..., use_skip_connection: bool = ...) -> None: ...
    def forward(self, x): ...

class SearchableFuseableSkipConv(SearchableConv2d):
    def __init__(self, in_channels: int, out_channels: int, stride: Union[int, Tuple[int, int]] = ..., use_skip_connection: bool = ...) -> None: ...
