from typing import Generator

from course_work.core.data.lexemes import Lexeme
from course_work.core.models.FiniteStateMachine import FiniteStateMachine
from course_work.core.data.LexicalTable import LexicalTable


class LexicalAnalyzer(FiniteStateMachine):
    def __init__(self,
                 states: dict[str, dict[str, list[str | bool | None]]],
                 lexical_table: dict[str, list[str]],
                 symbol_generator: Generator[str, None, None],
                 initial_state: str = "IN",
                 ):
        super().__init__(
            states,
            symbol_generator,
            initial_state,
        )
        self.lexical_table = LexicalTable(lexical_table)
        self.current_lexeme: None | tuple[int, int, int] = None
        self.current_lexeme_is_completed = False


    def add_number(self):
        token = self.accumulator
        self.lexical_table.add_number(token)
        self.current_lexeme = self.lexical_table.get_lexeme_tuple(token, self.pointer - len(token) - 1)
        self.current_lexeme_is_completed = True
        self.accumulator = ""

    def add_limiter(self):
        token = self.accumulator
        self.current_lexeme = self.lexical_table.get_lexeme_tuple(token, self.pointer - len(token))
        self.current_lexeme_is_completed = True
        self.accumulator = ""

    def add_identifier(self):
        token = self.accumulator
        if not self.lexical_table.check_identifier_is_keyword(token):
            self.lexical_table.add_identifier(token)
        self.current_lexeme = self.lexical_table.get_lexeme_tuple(token, self.pointer - len(token) - 1)
        self.current_lexeme_is_completed = True
        self.accumulator = ""

    def handle_finish(self):
        self.current_lexeme = self.lexical_table.get_lexeme_tuple("@", self.pointer - 1)
        self.current_lexeme_is_completed = True

    def make_step(self):
        super().make_step()


class LexemeIterator:
    def __init__(self,
                 lexical_analyzer: LexicalAnalyzer,
                 ):
        self.lexical_analyzer = lexical_analyzer

    def next_lexeme(self) -> Lexeme:
        self.lexical_analyzer.current_lexeme_is_completed = False
        while not self.lexical_analyzer.current_lexeme_is_completed:
            self.lexical_analyzer.make_step()

        lexeme_tuple: tuple[int, int, int] = self.lexical_analyzer.current_lexeme
        lexeme: Lexeme = Lexeme(
            lexeme_type=self.lexical_analyzer.lexical_table.get_lexeme_type(lexeme_tuple),
            lexeme_value=self.lexical_analyzer.lexical_table.get_lexeme_value(lexeme_tuple),
            lexeme_pointer=lexeme_tuple[2]
        )

        return lexeme