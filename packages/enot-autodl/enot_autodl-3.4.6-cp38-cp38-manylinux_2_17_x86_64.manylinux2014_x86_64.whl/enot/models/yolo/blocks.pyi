import torch.nn as nn
import torch
from _typeshed import Incomplete
from typing import List, Optional, Union

class ConvBNActivation(nn.Module):
    conv: Incomplete
    bn: Incomplete
    act: Incomplete
    def __init__(self, conv: torch.nn.Conv2d, bn: torch.nn.BatchNorm2d, act: Optional[torch.nn.Module] = ...) -> None: ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
    def forward_fuse(self, x): ...

class Bottleneck(nn.Module):
    cv1: Incomplete
    cv2: Incomplete
    add: Incomplete
    def __init__(self, conv1: ConvBNActivation, conv2: ConvBNActivation, skip: bool) -> None: ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...

class BottleNecksSequence(nn.Module):
    body: Incomplete
    def __init__(self, bottlenecks: Union[nn.Sequential, List[Bottleneck]]) -> None: ...
    @property
    def bottlenecks_count(self) -> int: ...
    @property
    def width_expansion(self) -> float: ...
    @property
    def args(self): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...

class C3(nn.Module):
    cv1: Incomplete
    cv2: Incomplete
    cv3: Incomplete
    bottle: Incomplete
    def __init__(self, cv1: ConvBNActivation, cv2: ConvBNActivation, cv3: ConvBNActivation, bottlenecks: BottleNecksSequence) -> None: ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...

class RepVGGBlock(nn.Module):
    nonlinearity: Incomplete
    rbr_identity: Incomplete
    rbr_dense: Incomplete
    rbr_1x1: Incomplete
    def __init__(self, skip_bn: nn.BatchNorm2d, rbr_dense: ConvBNActivation, rbr_1x1: ConvBNActivation, activation: nn.Module) -> None: ...
    def forward(self, inputs: torch.Tensor) -> torch.Tensor: ...

class BepC3(nn.Module):
    cv1: Incomplete
    cv2: Incomplete
    cv3: Incomplete
    concat: Incomplete
    m: Incomplete
    def __init__(self, cv1: nn.Module, cv2: nn.Module, cv3: nn.Module, m: nn.Module, concat: bool = ...) -> None: ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...

class BottleRepVgg(nn.Module):
    cv1: Incomplete
    cv2: Incomplete
    def __init__(self, cv1: nn.Module, cv2: nn.Module) -> None: ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
