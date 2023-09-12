import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from torch import nn
from typing import Any, Dict, List, Optional, Tuple, Type

LCALC_REGISTRY: Incomplete

class LatencyCalculator(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def calculate(self, model: nn.Module, inputs: Tuple, keyword_inputs: Optional[Dict[str, Any]] = ..., ignore_modules: Optional[List[Type[nn.Module]]] = ..., **options) -> float: ...

class MacCalculator(LatencyCalculator):
    def calculate(self, model: nn.Module, inputs: Tuple, keyword_inputs: Optional[Dict[str, Any]] = ..., ignore_modules: Optional[List[Type[nn.Module]]] = ..., **options) -> float: ...

class MacCalculatorThop(MacCalculator):
    def calculate(self, model: nn.Module, inputs: Tuple, keyword_inputs: Optional[Dict[str, Any]] = ..., ignore_modules: Optional[List[Type[nn.Module]]] = ..., **options) -> float: ...

class MacCalculatorPthflops(MacCalculator):
    def calculate(self, model: nn.Module, inputs: Tuple, keyword_inputs: Optional[Dict[str, Any]] = ..., ignore_modules: Optional[List[Type[nn.Module]]] = ..., **options) -> float: ...

class MacCalculatorFvcore(MacCalculator):
    def __init__(self, **kwargs) -> None: ...
    def calculate(self, model: nn.Module, inputs: Tuple, keyword_inputs: Optional[Dict[str, Any]] = ..., ignore_modules: Optional[List[Type[nn.Module]]] = ..., **options) -> float: ...
