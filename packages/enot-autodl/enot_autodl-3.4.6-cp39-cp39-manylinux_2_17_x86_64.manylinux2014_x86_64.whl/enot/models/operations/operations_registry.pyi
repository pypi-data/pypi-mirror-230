from _typeshed import Incomplete
from typing import Any, Callable, Dict, Optional, Tuple

GLOBAL_ACTIVATION_FUNCTION_REGISTRY: Incomplete

def reg_activation_class(activation_class): ...
reg_activation_class_decorator = reg_activation_class
SEARCHABLE_OPS_REGISTRY: Incomplete

def register_searchable_op(op_name: str, param_descriptions: Optional[Dict[str, Tuple[str, Callable[[str], Any]]]] = ...): ...
def get_searchable_op_class_with_params(op_name_with_params: str): ...
