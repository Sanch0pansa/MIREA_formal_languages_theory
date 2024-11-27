from course_work.core.data.lexemes import (
    LexemeType,
    LexemeTableType,
)

# Class of lexical table
class LexicalTable:
    keywords: list[str]
    limiters: list[str]
    numbers: list[str]
    identifiers: list[str]

    def __init__(self, table: dict[str, list[str]]):
        """
        Initialize lexical table

        :param table: lexical table dict with 4 keys: keywords, limiters, numbers, identifiers
        """

        # Trying to parse lexical table file, raise exception if can not
        try:
            self.keywords = table['keywords']
            self.limiters = table['limiters']
            self.numbers = table['numbers']
            self.identifiers = table['identifiers']
        except Exception as e:
            raise Exception("Wrong lexical table format")

    def check_identifier_is_keyword(self, identifier: str) -> bool:
        """
        Check if identifier is keyword

        :param identifier: identifier string
        :return: if identifier is keyword
        """
        return identifier in self.keywords

    def add_identifier(self, identifier: str):
        """
        Add identifier to lexical table

        :param identifier: new identifier to add
        """
        if identifier not in self.identifiers:
            self.identifiers.append(identifier)

    def add_number(self, number: str):
        """
        Add number to lexical table

        :param number: new number to add
        """
        if number not in self.numbers:
            self.numbers.append(number)

    def get_lexeme_tuple(self, lexeme_string: str, pointer: int) -> tuple[int, int, int]:
        """
        Get lexeme tuple by lexeme string

        :param lexeme_string: Lexeme string
        :param pointer: pointer of lexeme in original program text
        :return: lexeme table number, lexeme number in table, pointer to lexeme in table
        """
        lexeme_table_number: int = 1
        lexeme_number: int = 0
        if lexeme_string in self.keywords:
            lexeme_table_number = 1
            lexeme_number = self.keywords.index(lexeme_string)
        elif lexeme_string in self.limiters:
            lexeme_table_number = 2
            lexeme_number = self.limiters.index(lexeme_string)
        elif lexeme_string in self.numbers:
            lexeme_table_number = 3
            lexeme_number = self.numbers.index(lexeme_string)
        elif lexeme_string in self.identifiers:
            lexeme_table_number = 4
            lexeme_number = self.identifiers.index(lexeme_string)

        return lexeme_table_number, lexeme_number, pointer

    def get_lexeme_type(self, lexeme_tuple: tuple[int, int, int]) -> LexemeType:
        """
        Get type of provided lexeme

        :param lexeme_tuple: tuple representing lexeme
        :return: LexemeType value of provided lexeme
        """
        lexeme_table_number = LexemeTableType(lexeme_tuple[0])
        lexeme_position_in_table = lexeme_tuple[1]
        if lexeme_table_number == LexemeTableType.KEYWORDS:
            return LexemeType(lexeme_position_in_table)
        if lexeme_table_number == LexemeTableType.LIMITERS:
            return LexemeType(len(self.keywords) + lexeme_position_in_table)
        if lexeme_table_number == LexemeTableType.NUMBERS:
            return LexemeType.NUMBER
        if lexeme_table_number == LexemeTableType.IDENTIFIERS:
            return LexemeType.IDENTIFIER
        raise Exception(f"Unknown lexeme, {lexeme_tuple}")

    def get_lexeme_value(self, lexeme_tuple: tuple[int, int, int]) -> str:
        """
        Get string value of provided lexeme

        :param lexeme_tuple: tuple representing lexeme
        :return: string value of provided lexeme
        """
        lexeme_table_number = LexemeTableType(lexeme_tuple[0])
        lexeme_position_in_table = lexeme_tuple[1]
        if lexeme_table_number == LexemeTableType.KEYWORDS:
            return self.keywords[lexeme_position_in_table]
        if lexeme_table_number == LexemeTableType.LIMITERS:
            return self.limiters[lexeme_position_in_table]
        if lexeme_table_number == LexemeTableType.NUMBERS:
            return self.numbers[lexeme_position_in_table]
        if lexeme_table_number == LexemeTableType.IDENTIFIERS:
            return self.identifiers[lexeme_position_in_table]
        raise Exception(f"Unknown lexeme, {lexeme_tuple}")