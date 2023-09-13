from _typeshed import Incomplete
from torch import nn
from typing import Optional

class SearchableResNetD(nn.Module):
    in_channels: Incomplete
    out_channels: Incomplete
    expand_ratio: Incomplete
    expand_kernel_size: Incomplete
    squeeze_kernel_size: Incomplete
    stride: Incomplete
    padding: Incomplete
    block_operations: Incomplete
    use_skip_connection: Incomplete
    def __init__(self, in_channels: int, out_channels: int, hidden_channels: Optional[int] = ..., expand_ratio: Optional[float] = ..., squeeze_kernel_size: int = ..., expand_kernel_size: int = ..., stride: int = ..., padding: Optional[int] = ..., activation: str = ..., use_skip_connection: bool = ...) -> None: ...
    def forward(self, x): ...

class SearchableResNetE(nn.Module):
    in_channels: Incomplete
    out_channels: Incomplete
    expand_ratio: Incomplete
    expand_kernel_size: Incomplete
    squeeze_kernel_size: Incomplete
    stride: Incomplete
    padding: Incomplete
    block_operations: Incomplete
    use_skip_connection: Incomplete
    def __init__(self, in_channels: int, out_channels: int, hidden_channels: Optional[int] = ..., expand_ratio: Optional[float] = ..., squeeze_kernel_size: int = ..., expand_kernel_size: int = ..., stride: int = ..., padding: Optional[int] = ..., activation: str = ..., use_skip_connection: bool = ...) -> None: ...
    def forward(self, x): ...
