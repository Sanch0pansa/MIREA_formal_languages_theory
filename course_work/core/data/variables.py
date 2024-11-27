from dataclasses import dataclass
from enum import Enum


# Type of variables
class VariableType(Enum):
    TYPE_INT = "int"
    TYPE_FLOAT = "float"
    TYPE_BOOL = "bool"

# Class for variable
@dataclass
class Variable:
    variable_name: str
    variable_type: VariableType