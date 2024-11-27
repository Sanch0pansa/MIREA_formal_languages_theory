from win32file import TF_REUSE_SOCKET

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

    def raise_exception(self, message: str, lexeme: Lexeme | None = None):
        raise ASTException(
            message=message,
            lexeme=lexeme if lexeme else self.starting_lexeme
        )

    def semantic_check(self) -> None:
        pass


class ProgramNode(Node):
    description_nodes: list["DescriptionNode"] = []
    operator_nodes: list[type["OperatorNode"]] = []

    def add_description_node(self, description_node):
        self.description_nodes.append(description_node)

    def add_operator_node(self, operator_node):
        self.operator_nodes.append(operator_node)

    def semantic_check(self) -> None:
        for node in self.description_nodes:
            node.semantic_check()
        for node in self.operator_nodes:
            node.semantic_check()


class DescriptionNode(Node):
    variable_type_lexeme: Lexeme

    def set_variable_type_lexeme(self, variable_type_lexeme: Lexeme):
        self.variable_type_lexeme = variable_type_lexeme

    def add_variable(self, variable_lexeme: Lexeme):
        if self.tree.check_variable_exists(variable_lexeme.lexeme_value):
            self.raise_exception("Переменная объявлена ранее!")
        self.tree.add_variable(
            variable_lexeme=variable_lexeme,
            variable_type_lexeme=self.variable_type_lexeme
        )


class OperatorNode(Node):
    pass


class CompositeOperatorNode(OperatorNode):
    operator_nodes: list[type["OperatorNode"]] = []

    def add_operator_node(self, operator_node):
        self.operator_nodes.append(operator_node)

    def semantic_check(self) -> None:
        for node in self.operator_nodes:
            node.semantic_check()


class AssignmentOperatorNode(OperatorNode):
    identifier_variable: Variable
    expression_node: type["ExpressionNode"]

    def set_identifier(self, identifier_lexeme: Lexeme):
        self.identifier_variable = self.tree.get_variable(identifier_lexeme.lexeme_value)

    def set_expression_node(self, expression_node: type["ExpressionNode"]):
        self.expression_node = expression_node

    def semantic_check(self) -> bool:
        return self.identifier_variable.variable_type == self.expression_node.get_variable_type()


class ExpressionNode(Node):
    operand_nodes: list[type["OperandNode"]]
    operation_lexemes: list[Lexeme]

    def add_operand_node(self, operand_node: type["OperandNode"]):
        self.operand_nodes.append(operand_node)

    def add_operation_lexeme(self, operation_lexeme: Lexeme):
        self.operation_lexemes.append(operation_lexeme)

    def get_variable_type(self):
        return self.operand_nodes[0].get_variable_type()

    def semantic_check(self):
        for i in range(len(self.operation_lexemes)):
            operation_lexeme_type = self.operation_lexemes[i].lexeme_type
            type_equals = self.operand_nodes[i].get_variable_type() == self.operand_nodes[i + 1].get_variable_type()
            if not type_equals:
                self.raise_exception("Типы сравниваемых переменных должны совпадать")
            operand_type = self.operand_nodes[i].get_variable_type()
            if operation_lexeme_type in [
                LexemeType.LIM_LT,
                LexemeType.LIM_LTE,
                LexemeType.LIM_GT,
                LexemeType.LIM_GTE
            ]:
                if operand_type not in [VariableType.TYPE_FLOAT, VariableType.TYPE_INT]:
                    self.raise_exception(
                        "Операции отношений \">\", \"<\", \">=\", \"<=\" поддерживают сравнения только для операндов типов \"int\" и \"float\"",
                        self.operation_lexemes[i]
                    )
        for operand in self.operand_nodes:
            operand.semantic_check()


class OperandNode(Node):
    term_nodes: list[type["TermNode"]]
    operation_lexemes: list[Lexeme]

    def add_term_node(self, term_node: type["TermNode"]):
        self.term_nodes.append(term_node)

    def add_operation_lexeme(self, operation_lexeme: Lexeme):
        self.operation_lexemes.append(operation_lexeme)

    def get_variable_type(self):
        return self.term_nodes[0].get_variable_type()

    def semantic_check(self):
        for i in range(len(self.operation_lexemes)):
            operation_lexeme_type = self.operation_lexemes[i].lexeme_type
            type_equals = self.term_nodes[i].get_variable_type() == self.term_nodes[i + 1].get_variable_type()
            if not type_equals:
                self.raise_exception("Типы операндов операций \"+\", \"-\", \"||\" должны совпадать")
            operand_type = self.term_nodes[i].get_variable_type()
            if operation_lexeme_type in [
                LexemeType.LIM_PLUS,
                LexemeType.LIM_MINUS,
            ]:
                if operand_type not in [VariableType.TYPE_FLOAT, VariableType.TYPE_INT]:
                    self.raise_exception(
                        "Операции \"+\", \"-\" поддерживаются только для операндов типов \"int\" и \"float\"",
                        self.operation_lexemes[i]
                    )
            if operation_lexeme_type in [
                LexemeType.LIM_OR
            ]:
                if operand_type not in [VariableType.TYPE_BOOL]:
                    self.raise_exception(
                        "Операция \"||\" поддерживается только для операндов типа \"bool\"",
                        self.operation_lexemes[i]
                    )
        for term in self.term_nodes:
            term.semantic_check()


class TermNode(Node):
    factor_nodes: list[type["FactorNode"]]
    operation_lexemes: list[Lexeme]

    def add_factor_node(self, term_node: type["FactorNode"]):
        self.factor_nodes.append(term_node)

    def add_operation_lexeme(self, operation_lexeme: Lexeme):
        self.operation_lexemes.append(operation_lexeme)

    def get_variable_type(self):
        return self.factor_nodes[0].get_variable_type()

    def semantic_check(self):
        for i in range(len(self.operation_lexemes)):
            operation_lexeme_type = self.operation_lexemes[i].lexeme_type
            type_equals = self.factor_nodes[i].get_variable_type() == self.factor_nodes[i + 1].get_variable_type()
            if not type_equals:
                self.raise_exception("Типы операндов операций \"*\", \"/\", \"&&\" должны совпадать")
            operand_type = self.factor_nodes[i].get_variable_type()
            if operation_lexeme_type in [
                LexemeType.LIM_MUL,
                LexemeType.LIM_DIV,
            ]:
                if operand_type not in [VariableType.TYPE_FLOAT, VariableType.TYPE_INT]:
                    self.raise_exception(
                        "Операции \"*\", \"/\" поддерживаются только для операндов типов \"int\" и \"float\"",
                        self.operation_lexemes[i]
                    )
            if operation_lexeme_type in [
                LexemeType.LIM_AND
            ]:
                if operand_type not in [VariableType.TYPE_BOOL]:
                    self.raise_exception(
                        "Операция \"&&\" поддерживается только для операндов типа \"bool\"",
                        self.operation_lexemes[i]
                    )
        for factor in self.factor_nodes:
            factor.semantic_check()


class FactorNode(Node):
    value: Variable | type["UnaryOperationNode"] | type["ExpressionNode"]

    def set_value(self, value: Lexeme | type["UnaryOperationNode"] | type["ExpressionNode"]):
        if isinstance(value, Lexeme):
            if self.tree.check_variable_exists(value.lexeme_value):
                self.value = self.tree.get_variable(value.lexeme_value)
            else:
                self.raise_exception("Неизвестная переменная!", value)
        else:
            self.value = value

    def get_variable_type(self):
        if isinstance(self.value, Variable):
            return self.value.variable_type
        return self.value.get_variable_type()


    def semantic_check(self):
        if not isinstance(self.value, Variable):
            self.value.semantic_check()


class UnaryOperationNode(Node):
    value: type["FactorNode"]

    def set_value(self, value: type["FactorNode"]):
        self.value = value

    def semantic_check(self) -> None:
        if self.value.get_variable_type() != VariableType.TYPE_BOOL:
            self.raise_exception(
                "Операция \"!\" поддерживается только для операнда типа \"bool\"",
            )



class AbstractSyntaxTree:
    def __init__(self):

        self.variables_dict: dict = {}
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