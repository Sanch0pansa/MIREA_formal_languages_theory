from course_work.core.data.LexicalTable import LexicalTable
from course_work.core.data.lexemes import (
    Lexeme
)


# Class of lexical chain
class LexicalChain:
    def __init__(self,
                 chain: list[tuple[int, int, int]],
                 lexical_table: LexicalTable
                 ):
        """
        Initialize lexical chain

        :param chain: lexical chain presented as list of lexemes, presented as tuple
        """
        self.chain = chain                  # Chain presented as list of tuples
        self.lexical_table = lexical_table  # Object of LexicalTable

        self.pointer = 0                    # Pointer of current lexeme

    def add_lexeme(self, lexeme_tuple: tuple[int, int, int]):
        """
        Add lexeme to chain

        :param lexeme_tuple: tuple representing lexeme
        """
        self.chain.append(lexeme_tuple)

    def next_lexeme(self) -> Lexeme:
        """
        Get next lexeme in chain

        :return: next Lexeme
        """
        lexeme_tuple: tuple[int, int, int] = self.chain[self.pointer]
        lexeme: Lexeme = Lexeme(
            lexeme_type=self.lexical_table.get_lexeme_type(lexeme_tuple),
            lexeme_value=self.lexical_table.get_lexeme_value(lexeme_tuple),
            lexeme_pointer=lexeme_tuple[2]
        )
        self.pointer += 1
        return lexeme
