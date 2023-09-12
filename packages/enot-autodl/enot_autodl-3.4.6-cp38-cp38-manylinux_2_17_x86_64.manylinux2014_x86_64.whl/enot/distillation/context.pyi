from contextlib import ContextDecorator
from enot.distillation.mapping import Mapping
from torch import nn
from torch.fx.graph_module import GraphModule
from typing import Optional, Union

class distill(ContextDecorator):
    def __init__(self, teacher: Union[nn.Module, GraphModule], student: Union[nn.Module, GraphModule], mapping: Optional[Mapping] = ..., nograd_teacher: bool = ...) -> None: ...
    def __enter__(self) -> nn.Module: ...
    def __exit__(self, exc_type, exc_value, exc_traceback) -> None: ...
