from typing import Optional, Union
from course_work.core.data.variables import Variable, VariableType
from course_work.core.data.lexemes import LexemeType, Lexeme


class ASTException(Exception):
    def __init__(self, message: str, lexeme: Lexeme | None = None, *args):
        self.lexeme = lexeme
        self.message = message
        super().__init__(self.message, *args)


class Node:
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        self.starting_lexeme = starting_lexeme
        self.tree = tree
        self.children = {
            "children": []
        }

    def raise_exception(self, message: str, lexeme: Lexeme | None = None):
        raise ASTException(
            message=message,
            lexeme=lexeme if lexeme else self.starting_lexeme
        )

    def semantic_check(self) -> None:
        for key in self.children:
            if isinstance(self.children[key], Node):
                self.children[key].semantic_check()
            elif isinstance(self.children[key], list):
                for child in self.children[key]:
                    if isinstance(child, Node):
                        child.semantic_check()

    def get_title(self):
        return self.__class__.__name__

    def get_value_type(self) -> VariableType:
        return VariableType.TYPE_INT

    def to_string(self, indent=0):
        s = " " * indent + self.get_title()
        if self.children:
            s += "(\n"
            for key in self.children:
                if isinstance(self.children[key], Node):
                    s += " " * (indent + 1) + f"{key}:\n" + self.children[key].to_string(indent + 2)
                elif isinstance(self.children[key], list):
                    if self.children[key]:
                        s += " " * (indent + 1) + f"{key}: (\n"
                        for child in self.children[key]:
                            if isinstance(child, Node):
                                s += child.to_string(indent + 2)
                            elif isinstance(child, Lexeme):
                                s += " " * (indent + 2) + f"Lexeme({child.lexeme_value})"
                        s += " " * (indent + 1) + ")\n"
                elif isinstance(self.children[key], Lexeme):
                    s += " " * (indent + 1) + f"{key}: Lexeme({self.children[key].lexeme_value})"
            s += " " * indent + ")" + self.__class__.__name__ + "End\n"

        return s


class ProgramNode(Node):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "descriptions": [],
            "operators": [],
        }

    def add_description_node(self, description_node):
        self.children['descriptions'].append(description_node)

    def add_operator_node(self, operator_node):
        self.children['operators'].append(operator_node)


class DescriptionNode(Node):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.variable_type_lexeme: Lexeme = None
        self.variables_names: list[str] = []

    def set_variable_type_lexeme(self, variable_type_lexeme: Lexeme):
        self.variable_type_lexeme = variable_type_lexeme

    def add_variable(self, variable_lexeme: Lexeme):
        if self.tree.check_variable_exists(variable_lexeme.lexeme_value):
            self.raise_exception("Переменная объявлена ранее!")
        self.variables_names.append(variable_lexeme.lexeme_value)
        self.tree.add_variable(
            variable_lexeme=variable_lexeme,
            variable_type_lexeme=self.variable_type_lexeme
        )

    def get_title(self):
        s = "DescriptionNode" + "[" + self.variable_type_lexeme.lexeme_value + "]\tvariables: "
        s += "; ".join(name for name in self.variables_names) + "\n"
        return s

    def to_string(self, indent=0):
        return " " * indent + self.get_title()


class OperatorNode(Node):
    pass


class CompositeOperatorNode(OperatorNode):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "operators": []
        }

    def add_operator_node(self, operator_node):
        self.children['operators'].append(operator_node)

class ConditionalOperatorNode(OperatorNode):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "if": None,
            "then": None,
            "else": None,
        }

    def set_condition_expression_node(self, condition_expression_node):
        self.children['if'] = condition_expression_node

    def set_if_operator(self, if_operator):
        self.children['then'] = if_operator

    def set_else_operator(self, else_operator):
        self.children['else'] = else_operator

    def semantic_check(self) -> None:
        super().semantic_check()
        if self.children['if'] is None:
            self.raise_exception("Условный оператор должен иметь выражение")
        if isinstance(self.children['if'], Node) and self.children['if'].get_value_type() != VariableType.TYPE_BOOL:
            self.raise_exception("Выражение условного оператора должно возвращать значение типа \"bool\"")


class ConditionalLoopOperatorNode(OperatorNode):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "while": None,
            "do": None,
        }

    def set_condition_expression_node(self, condition_expression_node):
        self.children['while'] = condition_expression_node

    def set_while_operator(self, while_operator):
        self.children['do'] = while_operator

    def semantic_check(self) -> None:
        super().semantic_check()
        if self.children['while'].get_value_type() != VariableType.TYPE_BOOL:
            self.raise_exception("Выражение оператора условного цикла должно возвращать значение типа \"bool\"")


class FixedLoopOperatorNode(OperatorNode):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "for": None,
            "to": None,
            "step": None,
            "do": None
        }

    def set_assignment_operator_node(self, assignment_operator_node):
        self.children['for'] = assignment_operator_node

    def set_condition_expression_node(self, condition_expression_node):
        self.children['to'] = condition_expression_node

    def set_step_expression_node(self, step_expression_node):
        self.children['step'] = step_expression_node

    def set_operator_node(self, operator_node):
        self.children['do'] = operator_node

    def semantic_check(self) -> None:
        super().semantic_check()
        if isinstance(self.children['to'], Node) and self.children['to'].get_value_type() == VariableType.TYPE_BOOL:
            self.raise_exception("Выражение оператора условного цикла должно возвращать значение типа \"int\"")


class AssignmentOperatorNode(OperatorNode):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "expression": None
        }

        self.identifier_variable = None

    def set_identifier(self, identifier_lexeme: Lexeme):
        if not self.tree.check_variable_exists(identifier_lexeme.lexeme_value):
            self.raise_exception("Неизвестная переменная!")
        self.identifier_variable = self.tree.get_variable(identifier_lexeme.lexeme_value)

    def set_expression_node(self, expression_node: "ExpressionNode"):
        self.children['expression'] = expression_node

    def semantic_check(self):
        super().semantic_check()
        if self.identifier_variable.variable_type != self.children['expression'].get_value_type():
            self.raise_exception("Несоответствие типов переменной и значения выражения")
        self.tree.add_variable_value(self.identifier_variable.variable_name)

    def get_title(self):
        return f"AssignmentOperator:\t{self.identifier_variable.variable_name} := "


class OperationsNode(Node):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "operands": [],
            "operations": [],
        }

        self.operations_config = {
            LexemeType.LIM_EQ.value: {
                "first": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "second": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "return": "first",  # can be first/second/VariableType
            }
        }

    def semantic_check(self):
        super().semantic_check()
        for i in range(len(self.children['operations'])):
            operation_lexeme_type = self.children['operations'][i].lexeme_type
            type_equals = self.children['operands'][i].get_value_type() == self.children['operands'][i + 1].get_value_type()
            if not type_equals:
                self.raise_exception("Типы операндов должны совпадать")
            first_operand_type = self.children['operands'][i].get_value_type()
            second_operand_type = self.children['operands'][i + 1].get_value_type()

            if operation_lexeme_type.value in self.operations_config:
                correct_first_operand = any(
                    variable_type == first_operand_type for variable_type in
                    self.operations_config[operation_lexeme_type.value]["first"]
                )
                if not correct_first_operand:
                    first_operand_types = ", ".join(t.value for t in
                                                    self.operations_config[operation_lexeme_type.value]["first"])
                    self.raise_exception(f"Операция \"{self.children['operations'][i].lexeme_value}\" поддерживает для "
                                         f"первого операнда только типы: {first_operand_types}")
                correct_second_operand = any(
                    variable_type == second_operand_type for variable_type in
                    self.operations_config[operation_lexeme_type.value]["second"]
                )
                if not correct_second_operand:
                    second_operand_types = ", ".join(t.value for t in
                                                     self.operations_config[operation_lexeme_type.value]["second"])
                    self.raise_exception(f"Операция \"{self.children['operations'][i].lexeme_value}\" поддерживает для "
                                         f"второго операнда только типы: {second_operand_types}")

    def get_value_type(self):
        if len(self.children['operands']) == 1:
            return self.children['operands'][0].get_value_type()
        else:
            operation_lexeme_type = self.children['operations'][0].lexeme_type
            if operation_lexeme_type.value in self.operations_config:
                if self.operations_config[operation_lexeme_type.value]['return'] == 'first':
                    return self.children['operands'][0].get_value_type()
                elif self.operations_config[operation_lexeme_type.value]['return'] == 'second':
                    return self.children['operands'][1].get_value_type()
                else:
                    return self.operations_config[operation_lexeme_type.value]['return']


class ExpressionNode(OperationsNode):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "operands": [],
            "operations": [],
        }

        self.operations_config = {
            LexemeType.LIM_LT.value: {
                "first": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "second": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "return": VariableType.TYPE_BOOL,
            },
            LexemeType.LIM_LTE.value: {
                "first": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "second": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "return": VariableType.TYPE_BOOL,
            },
            LexemeType.LIM_GT.value: {
                "first": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "second": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "return": VariableType.TYPE_BOOL,
            },
            LexemeType.LIM_GTE.value: {
                "first": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "second": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "return": VariableType.TYPE_BOOL,
            }
        }

    def add_operand_node(self, operand_node: "OperandNode"):
        self.children['operands'].append(operand_node)

    def add_operation_lexeme(self, operation_lexeme: Lexeme):
        self.children['operations'].append(operation_lexeme)


class OperandNode(OperationsNode):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "operands": [],
            "operations": [],
        }

        self.operations_config = {
            LexemeType.LIM_PLUS.value: {
                "first": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "second": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "return": "first",
            },
            LexemeType.LIM_MINUS.value: {
                "first": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "second": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "return": "first",
            },
            LexemeType.LIM_OR.value: {
                "first": [VariableType.TYPE_BOOL],
                "second": [VariableType.TYPE_BOOL],
                "return": VariableType.TYPE_BOOL,
            },
        }

    def add_term_node(self, term_node: "TermNode"):
        self.children['operands'].append(term_node)

    def add_operation_lexeme(self, operation_lexeme: Lexeme):
        self.children['operations'].append(operation_lexeme)


class TermNode(OperationsNode):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "operands": [],
            "operations": [],
        }

        self.operations_config = {
            LexemeType.LIM_MUL.value: {
                "first": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "second": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "return": "first",
            },
            LexemeType.LIM_DIV.value: {
                "first": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "second": [VariableType.TYPE_INT, VariableType.TYPE_FLOAT],
                "return": "first",
            },
            LexemeType.LIM_AND.value: {
                "first": [VariableType.TYPE_BOOL],
                "second": [VariableType.TYPE_BOOL],
                "return": VariableType.TYPE_BOOL,
            },
        }

    def add_factor_node(self, term_node: "FactorNode"):
        self.children['operands'].append(term_node)

    def add_operation_lexeme(self, operation_lexeme: Lexeme):
        self.children['operations'].append(operation_lexeme)


class FactorNode(Node):
    value: Union["Variable", "UnaryOperationNode", "ExpressionNode", bool, float, int]

    def set_value(self, value: Union[Lexeme, "UnaryOperationNode", "ExpressionNode"]):
        if isinstance(value, Lexeme):
            if value.lexeme_type in [LexemeType.K_TRUE, LexemeType.K_FALSE]:
                self.value = value.lexeme_type == LexemeType.K_TRUE
            elif value.lexeme_type == LexemeType.NUMBER:
                if "." in value.lexeme_value or "e" in value.lexeme_value:
                    self.value = float(value.lexeme_value)
                else:
                    self.value = int(value.lexeme_value)
            else:
                if self.tree.check_variable_exists(value.lexeme_value):
                    self.value = self.tree.get_variable(value.lexeme_value)
                else:
                    self.raise_exception("Неизвестная переменная!", value)
        else:
            self.value = value

    def get_value_type(self):
        if isinstance(self.value, Variable):
            return self.value.variable_type
        if isinstance(self.value, bool):
            return VariableType.TYPE_BOOL
        if isinstance(self.value, float):
            return VariableType.TYPE_FLOAT
        if isinstance(self.value, int):
            return VariableType.TYPE_INT
        return self.value.get_value_type()

    def semantic_check(self):
        if isinstance(self.value, Node):
            self.value.semantic_check()
        if isinstance(self.value, Variable):
            if not self.tree.check_variable_has_value(self.value.variable_name):
                self.raise_exception("Переменная использована до инициализации!")

    def to_string(self, indent=0):
        s = " " * indent + "FactorNode("
        if isinstance(self.value, ExpressionNode) or isinstance(self.value, ExpressionNode):
            s += "\n" + self.value.to_string(indent + 1) + " " * indent
        elif isinstance(self.value, Variable):
            s += f"[{self.get_value_type().value}]: Variable(" + self.value.variable_name + ")"
        else:
            s += f"[{self.get_value_type().value}]: " + str(self.value)
        s += ")FactorNodeEnd\n"
        return s


class UnaryOperationNode(Node):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)
        self.children = {
            "value": None
        }

    def set_value(self, value: "FactorNode"):
        self.children[value] = value

    def semantic_check(self) -> None:
        if self.children['value'].get_value_type() != VariableType.TYPE_BOOL:
            self.raise_exception(
                "Операция \"!\" поддерживается только для операнда типа \"bool\"",
            )
        self.children['value'].semantic_check()

    def get_value_type(self):
        return self.children['value'].get_value_type()


class ReadOperationNode(Node):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)
        self.children = {
            'values': []
        }

    def semantic_check(self) -> None:
        for value in self.children['values']:
            self.tree.add_variable_value(value.variable_name)

    def add_variable(self, variable_lexeme: Lexeme):
        if self.tree.check_variable_exists(variable_lexeme.lexeme_value):
            self.children['values'].append(Variable(
                variable_name=variable_lexeme.lexeme_value,
                variable_type=self.tree.get_variable(variable_lexeme.lexeme_value).variable_type
            ))
        else:
            self.raise_exception(
                "Неизвестная переменная!",
                lexeme=variable_lexeme
            )

    def to_string(self, indent=0):
        s = super().to_string(indent) + f", variables: "
        s += "; ".join(variable.variable_name for variable in self.children['values']) + "\n"

        return s


class WriteOperationNode(Node):
    def __init__(self, tree: "AbstractSyntaxTree", starting_lexeme: Lexeme):
        super().__init__(tree, starting_lexeme)

        self.children = {
            "expressions": []
        }

    def add_expression_node(self, expression_node: ExpressionNode):
        self.children['expressions'].append(expression_node)


class AbstractSyntaxTree:
    def __init__(self):

        self.variables_dict: dict = {}
        self.variables_with_values = set()
        self.root = None

    def add_variable(self,
                     variable_lexeme: Lexeme,
                     variable_type_lexeme: Lexeme,
                     ) -> None:
        """
        Add variable to variables list

        :param variable_lexeme: lexeme presenting variable
        :param variable_type_lexeme: lexeme presenting variable type (for example, "int")
        """
        variable = Variable(
            variable_name=variable_lexeme.lexeme_value,
            variable_type=(
                VariableType(variable_type_lexeme.lexeme_value)
            )
        )

        self.variables_dict[variable.variable_name] = variable

    def check_variable_exists(self, variable_name: str) -> bool:
        """
        Check if variable exists in variable list

        :param variable_name: name of variable to check
        :return: if variable exists or not
        """
        return variable_name in self.variables_dict

    def get_variable(self, variable_name: str) -> Variable:
        """
        Get variable by name

        :param variable_name: name of variable to get
        :return: variable by name
        """
        return self.variables_dict[variable_name]

    def add_variable_value(self, variable_name: str):
        """
        Add value to variable (initialize)

        :param variable_name: name of variable
        """
        self.variables_with_values.add(variable_name)

    def check_variable_has_value(self, variable_name: str) -> bool:
        """
        Check if variable has value

        :param variable_name: name of variable
        :return: if variable has value or not
        """

        return variable_name in self.variables_dict and variable_name in self.variables_with_values
