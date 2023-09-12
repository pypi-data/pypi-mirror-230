import torch
from enot.pruning.gate import ChannelGate as ChannelGate
from enot.pruning.graph_parsing.parser_state.parser_state import DimensionLabels as DimensionLabels
from enot.pruning.graph_parsing.utils import pretty_str_labels as pretty_str_labels
from enot.pruning.labels import Label as Label, LabelGroup as LabelGroup
from enot.pruning.pruning_info import ModelPruningInfo as ModelPruningInfo
from enot.tensor_trace import Node as Node, OpNode as OpNode, ParameterNode as ParameterNode
from enot.tensor_trace.tensor_link_utils import get_tensor_by_link_in_model as get_tensor_by_link_in_model
from enot.tensor_trace.tools import get_module_name_by_tracing_node as get_module_name_by_tracing_node, get_tracing_node_by_module_name as get_tracing_node_by_module_name
from enot.utils.common import getattr_complex as getattr_complex
from enot.utils.weights_manipulation.weight_mapping import apply_nd_mapping as apply_nd_mapping
from pathlib import Path
from torch import nn as nn
from typing import List, NamedTuple, Optional, Tuple, Union

class LabelFilterInfo(NamedTuple):
    tensor_name: str
    shape: Tuple[int, ...]
    mapping: List[Optional[List[Tuple[int, int]]]]
    tensor: Optional[torch.Tensor]

def tabulate_module_dependencies(module_name: str, pruning_info: ModelPruningInfo, model: Optional[nn.Module] = ..., show_op_with_weights_only: bool = ..., show_parameter_nodes: bool = ..., show_all_nodes: bool = ...) -> str: ...
def tabulate_label_dependencies(label: Union[Label, int], pruning_info: ModelPruningInfo, model: Optional[nn.Module] = ..., show_op_with_weights_only: bool = ..., show_parameter_nodes: bool = ..., show_all_nodes: bool = ...) -> str: ...
def tabulate_unprunable_groups(pruning_info: ModelPruningInfo, model: Optional[nn.Module] = ..., show_op_with_weights_only: bool = ..., show_parameter_nodes: bool = ..., show_all_nodes: bool = ...) -> str: ...
def tabulate_label_filters(label: Union[Label, int], pruning_info: ModelPruningInfo, model: nn.Module) -> str: ...
def get_label_filters(label: Union[Label, int], pruning_info: ModelPruningInfo, model: nn.Module, *, with_tensors: bool = ...) -> List[LabelFilterInfo]: ...
def save_pruning_info(pruning_info: ModelPruningInfo, path: Union[str, Path]) -> None: ...
def load_pruning_info(path: Union[str, Path]) -> ModelPruningInfo: ...
