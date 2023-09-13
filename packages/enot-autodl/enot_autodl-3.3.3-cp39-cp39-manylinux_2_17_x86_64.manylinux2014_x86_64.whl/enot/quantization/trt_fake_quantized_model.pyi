from _typeshed import Incomplete
from enot.quantization import FakeQuantizedModel
from torch import nn
from typing import List, Optional, Type, Union

class _QuantizationPatternsBuilder:
    w_qtype: Incomplete
    act_qtype: Incomplete
    def __init__(self, use_weight_scale_factors: bool, use_bias_scale_factors: bool, quantization_scheme: str) -> None: ...
    def build(self): ...

class TrtFakeQuantizedModel(FakeQuantizedModel):
    def __init__(self, model: nn.Module, leaf_modules: Optional[List[Union[Type[nn.Module], nn.Module]]] = ..., quantization_scheme: str = ..., use_weight_scale_factors: bool = ..., use_bias_scale_factors: bool = ..., inplace: bool = ...) -> None: ...
