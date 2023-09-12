from _typeshed import Incomplete
from torch import nn
from typing import Optional

class SearchableResNext(nn.Module):
    kernel_size: Incomplete
    cardinality: Incomplete
    expand_ratio: Incomplete
    stride: Incomplete
    padding: Incomplete
    in_channels: Incomplete
    out_channels: Incomplete
    hidden_channels: Incomplete
    block_operations: Incomplete
    use_skip_connection: Incomplete
    def __init__(self, in_channels: int, out_channels: int, hidden_channels: Optional[int] = ..., expand_ratio: Optional[float] = ..., kernel_size: int = ..., cardinality: int = ..., stride: int = ..., padding: Optional[int] = ..., activation: str = ..., use_skip_connection: bool = ...) -> None: ...
    def forward(self, x): ...
