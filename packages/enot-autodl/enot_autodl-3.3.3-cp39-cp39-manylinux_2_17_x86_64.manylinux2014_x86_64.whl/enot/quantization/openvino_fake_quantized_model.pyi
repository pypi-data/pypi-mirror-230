import torch.nn as nn
from _typeshed import Incomplete
from enot.quantization import FakeQuantizedModel
from typing import List, Optional, Type, Union

class _QuantizationPatternsBuilder:
    w_qtype: Incomplete
    act_qtype: Incomplete
    def __init__(self, apply_avx2_fix: bool, use_weight_scale_factors: bool, use_bias_scale_factors: bool) -> None: ...
    def build(self): ...

class OpenvinoFakeQuantizedModel(FakeQuantizedModel):
    def __init__(self, model: nn.Module, leaf_modules: Optional[List[Union[Type[nn.Module], nn.Module]]] = ..., apply_avx2_fix: bool = ..., use_weight_scale_factors: bool = ..., use_bias_scale_factors: bool = ..., inplace: bool = ..., **kwargs) -> None: ...
