from course_work.core.data.lexemes import (
    Lexeme,
    LexemeType,
)

from course_work.core.data.LexicalTable import (
    LexicalTable,
)

from course_work.core.models.AbstractSyntaxTree2 import (
    AbstractSyntaxTree,
    ProgramNode,
    DescriptionNode,
    CompositeOperatorNode,
    AssignmentOperatorNode,
    ConditionalOperatorNode,
    ConditionalLoopOperatorNode,
    FixedLoopOperatorNode,
    WriteOperationNode,
    ReadOperationNode,
    ExpressionNode,
    TermNode,
    OperandNode,
    FactorNode,
    UnaryOperationNode,
)
from course_work.core.parsers.LexicalAnalyzer import LexemeIterator


class SyntaxException(Exception):
    def __init__(self, message: str, lexeme: Lexeme | None = None, *args):
        self.lexeme = lexeme
        self.message = message
        super().__init__(self.message, *args)


# Syntax parser
class SyntaxAnalyzer:
    def __init__(self, lexical_table: LexicalTable, lexeme_iterator: LexemeIterator):
        self.lexical_table = lexical_table          # LexicalTable object
        self.lexeme_iterator = lexeme_iterator      # LexemeIterator object
        self.current_lexeme: Lexeme | None = None   # Current lexeme
        self.AST = AbstractSyntaxTree()

    def read_next_lexeme(self):
        """
        Read next lexeme and save it in current lexeme
        """
        self.current_lexeme = self.lexeme_iterator.next_lexeme()

    def check_current_lexeme(self, *args):
        """
        Checks lexeme corresponding provided type

        :param args: list of lexeme type options
        :return: true if lexeme corresponds at least one option else false
        """
        return any(self.current_lexeme.lexeme_type == lexeme_type for lexeme_type in args)

    def raise_exception(self, message):
        """
        Raises syntax exception

        :param message: Message of exception
        """
        raise SyntaxException(
            message,
            self.current_lexeme,
        )

    # Recursive functions
    def func_program(self):
        program_node = ProgramNode(
            self.AST,
            self.current_lexeme,
        )
        if self.check_current_lexeme(LexemeType.K_PROGRAM):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное начало программы!")
        if self.check_current_lexeme(LexemeType.K_VAR):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное начало описания!")

        program_node.add_description_node(self.func_description())
        while self.check_current_lexeme(LexemeType.LIM_SEMICOLON):
            self.read_next_lexeme()
            program_node.add_description_node(self.func_description())

        if self.check_current_lexeme(LexemeType.K_BEGIN):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное начало программы!")

        program_node.add_operator_node(self.func_operator())
        while self.check_current_lexeme(LexemeType.LIM_SEMICOLON):
            self.read_next_lexeme()
            program_node.add_operator_node(self.func_operator())

        if self.check_current_lexeme(LexemeType.K_END):
            pass
        else:
            self.raise_exception("Неверное завершение программы!")

        self.read_next_lexeme()

        if self.check_current_lexeme(LexemeType.LIM_END):
            pass
        else:
            self.raise_exception("Неверное завершение программы!")

        return program_node

    def func_description(self):
        description_node = DescriptionNode(
            self.AST,
            self.current_lexeme,
        )
        if self.check_current_lexeme(LexemeType.K_INT, LexemeType.K_FLOAT, LexemeType.K_BOOL):
            description_node.set_variable_type_lexeme(self.current_lexeme)
            self.read_next_lexeme()
        else:
            self.raise_exception(f"Неверное описание программы!")

        if self.check_current_lexeme(LexemeType.IDENTIFIER):
            description_node.add_variable(self.current_lexeme)
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное объявление типов!")

        while self.check_current_lexeme(LexemeType.LIM_COMMA):
            self.read_next_lexeme()
            if self.check_current_lexeme(LexemeType.IDENTIFIER):
                description_node.add_variable(self.current_lexeme)
                self.read_next_lexeme()
            else:
                self.raise_exception("Неверное объявление типов!")

        return description_node

    def func_operator(self):
        if self.check_current_lexeme(LexemeType.K_BEGIN):
            return self.func_composite_operator()
        elif self.check_current_lexeme(LexemeType.IDENTIFIER):
            return self.func_assignment_operator()
        elif self.check_current_lexeme(LexemeType.K_IF):
            return self.func_condition_operator()
        elif self.check_current_lexeme(LexemeType.K_FOR):
            return self.func_fixed_loop_operator()
        elif self.check_current_lexeme(LexemeType.K_WHILE):
            return self.func_conditional_loop_operator()
        elif self.check_current_lexeme(LexemeType.K_READLN):
            return self.func_read()
        elif self.check_current_lexeme(LexemeType.K_WRITELN):
            return self.func_write()
        else:
            self.raise_exception("Неверный синтаксис оператора!")

    def func_composite_operator(self):
        composite_operator_node = CompositeOperatorNode(
            self.AST,
            self.current_lexeme,
        )
        if self.check_current_lexeme(LexemeType.K_BEGIN):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное начало составного оператора!")

        composite_operator_node.add_operator_node(self.func_operator())
        while self.check_current_lexeme(LexemeType.LIM_SEMICOLON):
            self.read_next_lexeme()
            composite_operator_node.add_operator_node(self.func_operator())

        if self.check_current_lexeme(LexemeType.K_END):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное завершение составного оператора!")

        return composite_operator_node

    def func_assignment_operator(self):
        assignment_operator_node = AssignmentOperatorNode(
            self.AST,
            self.current_lexeme,
        )
        if not self.check_current_lexeme(LexemeType.IDENTIFIER):
            self.raise_exception("Неверное начало оператор присвоения!")
        assignment_operator_node.set_identifier(self.current_lexeme)
        self.read_next_lexeme()
        if not self.check_current_lexeme(LexemeType.LIM_ASSIGN):
            self.raise_exception("При присвоении после идентификатора должен следовать оператор присвоения!")
        self.read_next_lexeme()
        assignment_operator_node.set_expression_node(self.func_expression())

        return assignment_operator_node

    def func_condition_operator(self):
        condition_operator_node = ConditionalOperatorNode(
            self.AST,
            self.current_lexeme,
        )
        if not self.check_current_lexeme(LexemeType.K_IF):
            self.raise_exception("Неверное начало условного оператора!")
        self.read_next_lexeme()
        if not self.check_current_lexeme(LexemeType.LIM_OPEN_PAREN):
            self.raise_exception("Выражение условного оператора должно быть заключено в скобки!")
        self.read_next_lexeme()
        condition_operator_node.set_condition_expression_node(self.func_expression())
        if not self.check_current_lexeme(LexemeType.LIM_CLOSE_PAREN):
            self.raise_exception("Выражение условного оператора должно быть заключено в скобки!")
        self.read_next_lexeme()
        condition_operator_node.set_if_operator(self.func_operator())
        self.read_next_lexeme()
        if self.check_current_lexeme(LexemeType.K_ELSE):
            self.read_next_lexeme()
            condition_operator_node.set_else_operator(self.func_operator())

        return condition_operator_node

    def func_fixed_loop_operator(self):
        fixed_loop_operator_node = FixedLoopOperatorNode(
            self.AST,
            self.current_lexeme,
        )
        if not self.check_current_lexeme(LexemeType.K_FOR):
            self.raise_exception("Неверное начало оператора фиксированного цикла!")
        self.read_next_lexeme()
        fixed_loop_operator_node.set_assignment_operator_node(self.func_assignment_operator())
        if not self.check_current_lexeme(LexemeType.K_TO):
            self.raise_exception("Неверный синтаксис оператора фиксированного цикла!")
        self.read_next_lexeme()
        fixed_loop_operator_node.set_condition_expression_node(self.func_expression())
        if self.check_current_lexeme(LexemeType.K_STEP):
            self.read_next_lexeme()
            fixed_loop_operator_node.set_step_expression_node(self.func_expression())
        fixed_loop_operator_node.set_operator_node(self.func_operator())
        if not self.check_current_lexeme(LexemeType.K_NEXT):
            self.raise_exception("Неверное завершение оператора фиксированного цикла!")
        self.read_next_lexeme()

        return fixed_loop_operator_node

    def func_conditional_loop_operator(self):
        conditional_loop_operator_node = ConditionalLoopOperatorNode(
            self.AST,
            self.current_lexeme,
        )
        if not self.check_current_lexeme(LexemeType.K_WHILE):
            self.raise_exception("Неверное начало оператора условного цикла!")
        self.read_next_lexeme()
        if not self.check_current_lexeme(LexemeType.LIM_OPEN_PAREN):
            self.raise_exception("Выражение оператора условного цикла должно быть заключено в скобки!")
        self.read_next_lexeme()
        conditional_loop_operator_node.set_condition_expression_node(self.func_expression())
        if not self.check_current_lexeme(LexemeType.LIM_CLOSE_PAREN):
            self.raise_exception("Выражение оператора условного цикла должно быть заключено в скобки!")
        self.read_next_lexeme()
        conditional_loop_operator_node.set_while_operator(self.func_operator())
        self.read_next_lexeme()

        return conditional_loop_operator_node

    def func_read(self):
        read_operator_node = ReadOperationNode(
            self.AST,
            self.current_lexeme,
        )
        if self.check_current_lexeme(LexemeType.K_READLN):
            self.read_next_lexeme()
        else:
            self.raise_exception(f"Неверное начало оператора ввода!")

        if self.check_current_lexeme(LexemeType.IDENTIFIER):
            read_operator_node.add_variable(self.current_lexeme)
            self.read_next_lexeme()
        else:
            self.raise_exception("Оператор ввода должен принимать идентификаторы!")

        while self.check_current_lexeme(LexemeType.LIM_COMMA):
            self.read_next_lexeme()
            if self.check_current_lexeme(LexemeType.IDENTIFIER):
                read_operator_node.add_variable(self.current_lexeme)
                self.read_next_lexeme()
            else:
                self.raise_exception("Оператор ввода должен принимать идентификаторы!")

        return read_operator_node


    def func_write(self):
        write_operator_node = WriteOperationNode(
            self.AST,
            self.current_lexeme
        )
        if self.check_current_lexeme(LexemeType.K_WRITELN):
            self.read_next_lexeme()
        else:
            self.raise_exception(f"Неверное начало оператора вывода!")

        write_operator_node.add_expression_node(self.func_expression())

        while self.check_current_lexeme(LexemeType.LIM_COMMA):
            self.read_next_lexeme()
            write_operator_node.add_expression_node(self.func_expression())

        return write_operator_node

    def func_expression(self):
        expression_node = ExpressionNode(
            self.AST,
            self.current_lexeme
        )
        expression_node.add_operand_node(self.func_operand())
        while self.check_current_lexeme(
                LexemeType.LIM_EQ,
                LexemeType.LIM_NE,
                LexemeType.LIM_GT,
                LexemeType.LIM_GTE,
                LexemeType.LIM_LT,
                LexemeType.LIM_LTE):
            expression_node.add_operation_lexeme(self.current_lexeme)
            self.read_next_lexeme()
            expression_node.add_operand_node(self.func_operand())

        return expression_node

    def func_operand(self):
        operand_node = OperandNode(
            self.AST,
            self.current_lexeme
        )
        operand_node.add_term_node(self.func_term())
        while self.check_current_lexeme(
                LexemeType.LIM_PLUS,
                LexemeType.LIM_OR,
                LexemeType.LIM_MINUS):
            operand_node.add_operation_lexeme(self.current_lexeme)
            self.read_next_lexeme()
            operand_node.add_term_node(self.func_term())

        return operand_node

    def func_term(self):
        term_node = TermNode(
            self.AST,
            self.current_lexeme
        )
        term_node.add_factor_node(self.func_factor())
        while self.check_current_lexeme(
                LexemeType.LIM_MUL,
                LexemeType.LIM_DIV,
                LexemeType.LIM_AND):
            term_node.add_operation_lexeme(self.current_lexeme)
            self.read_next_lexeme()
            term_node.add_factor_node(self.func_factor())

        return term_node

    def func_factor(self):
        factor_node = FactorNode(
            self.AST,
            self.current_lexeme
        )
        if self.check_current_lexeme(LexemeType.IDENTIFIER):
            factor_node.set_value(self.current_lexeme)
            self.read_next_lexeme()
        elif self.check_current_lexeme(LexemeType.NUMBER):
            factor_node.set_value(self.current_lexeme)
            self.read_next_lexeme()
        elif self.check_current_lexeme(LexemeType.K_FALSE, LexemeType.K_TRUE):
            factor_node.set_value(self.current_lexeme)
            self.read_next_lexeme()
        elif self.check_current_lexeme(LexemeType.LIM_NOT):
            unary_operation_node = UnaryOperationNode(
                self.AST,
                self.current_lexeme
            )
            self.read_next_lexeme()
            unary_operation_node.set_value(self.func_factor())
        elif self.check_current_lexeme(LexemeType.LIM_OPEN_PAREN):
            self.read_next_lexeme()
            factor_node.set_value(self.func_expression())
            if not self.check_current_lexeme(LexemeType.LIM_CLOSE_PAREN):
                self.raise_exception("Открытая скобка в выражении должна быть закрыта!")
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверный синтаксис множителя!")

        return factor_node

    # Main parsing entrypoint
    def parse(self):
        self.read_next_lexeme()
        self.AST.root = self.func_program()