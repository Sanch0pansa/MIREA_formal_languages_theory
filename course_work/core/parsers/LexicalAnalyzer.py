from course_work.core.models.FiniteStateMachine import FiniteStateMachine
from course_work.core.data.LexicalTable import LexicalTable
from course_work.core.data.LexicalChain import LexicalChain


class LexicalAnalyzer(FiniteStateMachine):
    def __init__(self,
                 string: str,
                 states: dict[str, dict[str, list[str | bool | None]]],
                 lexical_table: dict[str, list[str]],
                 initial_state: str = "IN",
                 ):
        super().__init__(
            string,
            states,
            initial_state
        )
        self.lexical_table = LexicalTable(lexical_table)
        self.lexical_chain = LexicalChain(
            [],
            self.lexical_table
        )

    def add_number(self):
        token = self.accumulator
        self.lexical_table.add_number(token)
        self.lexical_chain.add_lexeme(
            self.lexical_table.get_lexeme_tuple(token, self.pointer - len(token) - 1)
        )
        self.accumulator = ""

    def add_limiter(self):
        token = self.accumulator
        self.lexical_chain.add_lexeme(
            self.lexical_table.get_lexeme_tuple(token, self.pointer - len(token))
        )
        self.accumulator = ""

    def add_identifier(self):
        token = self.accumulator
        if not self.lexical_table.check_identifier_is_keyword(token):
            self.lexical_table.add_identifier(token)
        self.lexical_chain.add_lexeme(
            self.lexical_table.get_lexeme_tuple(token, self.pointer - len(token) - 1)
        )
        self.accumulator = ""
