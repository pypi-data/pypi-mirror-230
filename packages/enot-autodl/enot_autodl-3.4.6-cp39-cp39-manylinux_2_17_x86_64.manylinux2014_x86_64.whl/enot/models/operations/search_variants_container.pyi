import torch.nn as nn
from _typeshed import Incomplete
from enot.models.operations.search_operations_container import SearchableOperationsContainer as SearchableOperationsContainer
from enot.utils.common import iterate_by_submodules as iterate_by_submodules
from typing import Any, Iterable, Optional

class SearchVariantsContainer(nn.Module):
    search_variants: Incomplete
    call_operation: Incomplete
    def __init__(self, search_variants: Iterable[nn.Module], default_operation_index: int = ..., **kwargs) -> None: ...
    def set_default_operation(self, operation_index: Optional[int]) -> None: ...
    def forward(self, *args, **kwargs) -> Any: ...
