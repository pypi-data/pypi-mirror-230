import torch.fx as fx
import torch
from enot.graph.transform_params import TransformationParameters
from typing import Any, Dict, List, Optional, Tuple, Type, Union

def generate_pruned_search_variants_model(model: torch.nn.Module, search_variant_descriptors: Optional[Tuple[TransformationParameters, ...]] = ..., excluded_modules: Optional[List[Union[Type[torch.nn.Module], torch.nn.Module]]] = ..., concrete_args: Optional[Dict[str, Any]] = ..., keep_debug_names: bool = ...) -> fx.GraphModule: ...
