from course_work.core.data.lexemes import (
    Lexeme,
    LexemeType,
)

from course_work.core.data.LexicalTable import (
    LexicalTable,
)

from course_work.core.data.LexicalChain import (
    LexicalChain,
)


class SyntaxException(Exception):
    def __init__(self, message: str, lexeme: Lexeme | None = None, *args):
        self.lexeme = lexeme
        self.message = message
        super().__init__(self.message, *args)


# Syntax parser
class SyntaxAnalyzer:
    def __init__(self, lexical_table: LexicalTable, lexical_chain: LexicalChain):
        self.lexical_table = lexical_table          # LexicalTable object
        self.lexical_chain = lexical_chain          # LexicalChain object
        self.current_lexeme: Lexeme | None = None   # Current lexeme
        self.stack: list[Lexeme] = []               # Stack of lexemes

    def read_next_lexeme(self):
        """
        Read next lexeme and save it in current lexeme
        """
        self.current_lexeme = self.lexical_chain.next_lexeme()

    def push_lexeme(self, lexeme: Lexeme):
        """
        Pushes lexeme to stack

        :param lexeme: lexeme to save
        """
        self.stack.append(lexeme)

    def pop_lexeme(self) -> Lexeme:
        """
        Return and delete last lexeme in stack

        :return: Lexeme: last saved lexeme
        """
        return self.stack.pop()

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
        if self.check_current_lexeme(LexemeType.K_PROGRAM):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное начало программы!")
        if self.check_current_lexeme(LexemeType.K_VAR):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное начало описания!")
        self.func_description()

        if self.check_current_lexeme(LexemeType.K_BEGIN):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное начало программы!")

        self.func_operator()
        while self.check_current_lexeme(LexemeType.LIM_SEMICOLON):
            self.read_next_lexeme()
            self.func_operator()

        if self.check_current_lexeme(LexemeType.K_END):
            pass
        else:
            self.raise_exception("Неверное завершение программы!")

    def func_description(self):
        if self.check_current_lexeme(LexemeType.K_INT, LexemeType.K_FLOAT, LexemeType.K_BOOL):
            self.read_next_lexeme()
        else:
            self.raise_exception(f"Неверное описание программы!")

        if self.check_current_lexeme(LexemeType.IDENTIFIER):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное объявление типов!")

        while self.check_current_lexeme(LexemeType.LIM_COMMA):
            self.read_next_lexeme()
            if self.check_current_lexeme(LexemeType.IDENTIFIER):
                self.read_next_lexeme()
            else:
                self.raise_exception("Неверное объявление типов!")

    def func_operator(self):
        if self.check_current_lexeme(LexemeType.K_BEGIN):
            self.func_composite_operator()
        elif self.check_current_lexeme(LexemeType.IDENTIFIER):
            self.func_assignment_operator()
        elif self.check_current_lexeme(LexemeType.K_IF):
            self.func_condition_operator()
        elif self.check_current_lexeme(LexemeType.K_FOR):
            self.func_fixed_loop_operator()
        elif self.check_current_lexeme(LexemeType.K_WHILE):
            self.func_conditional_loop_operator()
        elif self.check_current_lexeme(LexemeType.K_READLN):
            self.func_read()
        elif self.check_current_lexeme(LexemeType.K_WRITELN):
            self.func_write()
        else:
            self.raise_exception("Неверный синтаксис оператора!")

    def func_composite_operator(self):
        if self.check_current_lexeme(LexemeType.K_BEGIN):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное начало составного оператора!")

        self.func_operator()
        while self.check_current_lexeme(LexemeType.LIM_SEMICOLON):
            self.read_next_lexeme()
            self.func_operator()

        if self.check_current_lexeme(LexemeType.K_END):
            pass
        else:
            self.raise_exception("Неверное завершение составного оператора!")

    def func_assignment_operator(self):
        if not self.check_current_lexeme(LexemeType.IDENTIFIER):
            self.raise_exception("Неверное начало оператор присвоения!")
        self.read_next_lexeme()
        if not self.check_current_lexeme(LexemeType.LIM_ASSIGN):
            self.raise_exception("При присвоении после идентификатора должен следовать оператор присвоения!")
        self.read_next_lexeme()
        self.func_expression()

    def func_condition_operator(self):
        if not self.check_current_lexeme(LexemeType.K_IF):
            self.raise_exception("Неверное начало условного оператора!")
        self.read_next_lexeme()
        if not self.check_current_lexeme(LexemeType.LIM_OPEN_PAREN):
            self.raise_exception("Выражение условного оператора должно быть заключено в скобки!")
        self.read_next_lexeme()
        self.func_expression()
        if not self.check_current_lexeme(LexemeType.LIM_CLOSE_PAREN):
            self.raise_exception("Выражение условного оператора должно быть заключено в скобки!")
        self.read_next_lexeme()
        self.func_operator()
        self.read_next_lexeme()
        if self.check_current_lexeme(LexemeType.K_ELSE):
            self.read_next_lexeme()
            self.func_operator()

    def func_fixed_loop_operator(self):
        if not self.check_current_lexeme(LexemeType.K_FOR):
            self.raise_exception("Неверное начало оператора фиксированного цикла!")
        self.read_next_lexeme()
        self.func_assignment_operator()
        if not self.check_current_lexeme(LexemeType.K_TO):
            self.raise_exception("Неверный синтаксис оператора фиксированного цикла!")
        self.read_next_lexeme()
        self.func_expression()
        if self.check_current_lexeme(LexemeType.K_STEP):
            self.read_next_lexeme()
            self.func_expression()
        self.func_operator()
        if not self.check_current_lexeme(LexemeType.K_NEXT):
            self.raise_exception("Неверное завершение оператора фиксированного цикла!")
        self.read_next_lexeme()

    def func_conditional_loop_operator(self):
        if not self.check_current_lexeme(LexemeType.K_WHILE):
            self.raise_exception("Неверное начало оператора условного цикла!")
        self.read_next_lexeme()
        if not self.check_current_lexeme(LexemeType.LIM_OPEN_PAREN):
            self.raise_exception("Выражение оператора условного цикла должно быть заключено в скобки!")
        self.read_next_lexeme()
        self.func_expression()
        if not self.check_current_lexeme(LexemeType.LIM_CLOSE_PAREN):
            self.raise_exception("Выражение оператора условного цикла должно быть заключено в скобки!")
        self.read_next_lexeme()
        self.func_operator()
        self.read_next_lexeme()

    def func_read(self):
        if self.check_current_lexeme(LexemeType.K_READLN):
            self.read_next_lexeme()
        else:
            self.raise_exception(f"Неверное начало описания!")

        if self.check_current_lexeme(LexemeType.IDENTIFIER):
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверное объявление типов!")

        while self.check_current_lexeme(LexemeType.LIM_COMMA):
            self.read_next_lexeme()
            if self.check_current_lexeme(LexemeType.IDENTIFIER):
                self.read_next_lexeme()
            else:
                self.raise_exception("Неверное объявление типов!")

    def func_write(self):
        pass

    def func_expression(self):
        self.func_operand()
        while self.check_current_lexeme(
                LexemeType.LIM_EQ,
                LexemeType.LIM_NE,
                LexemeType.LIM_GT,
                LexemeType.LIM_GTE,
                LexemeType.LIM_LT,
                LexemeType.LIM_LTE):
            self.read_next_lexeme()
            self.func_operand()

    def func_operand(self):
        self.func_term()
        while self.check_current_lexeme(
                LexemeType.LIM_PLUS,
                LexemeType.LIM_OR,
                LexemeType.LIM_MINUS):
            self.read_next_lexeme()
            self.func_term()

    def func_term(self):
        self.func_factor()
        while self.check_current_lexeme(
                LexemeType.LIM_MUL,
                LexemeType.LIM_DIV,
                LexemeType.LIM_AND):
            self.read_next_lexeme()
            self.func_factor()

    def func_factor(self):
        if self.check_current_lexeme(LexemeType.IDENTIFIER):
            self.read_next_lexeme()
        elif self.check_current_lexeme(LexemeType.NUMBER):
            self.read_next_lexeme()
        elif self.check_current_lexeme(LexemeType.K_FALSE, LexemeType.K_TRUE):
            self.read_next_lexeme()
        elif self.check_current_lexeme(LexemeType.LIM_NOT):
            self.read_next_lexeme()
            self.func_factor()
        elif self.check_current_lexeme(LexemeType.LIM_OPEN_PAREN):
            self.read_next_lexeme()
            self.func_expression()
            if not self.check_current_lexeme(LexemeType.LIM_CLOSE_PAREN):
                self.raise_exception("Открытая скобка в выражении должна быть закрыта!")
            self.read_next_lexeme()
        else:
            self.raise_exception("Неверный синтаксис множителя!")

    # Main parsing entrypoint
    def parse(self):
        self.read_next_lexeme()
        self.func_program()