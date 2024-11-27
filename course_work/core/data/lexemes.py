from enum import Enum
from dataclasses import dataclass


# Lexeme type enum
class LexemeType(Enum):
    # Keywords
    K_TRUE = 0
    K_FALSE = 1
    K_PROGRAM = 2
    K_VAR = 3
    K_END = 4
    K_BEGIN = 5
    K_INT = 6
    K_FLOAT = 7
    K_BOOL = 8
    K_IF = 9
    K_ELSE = 10
    K_FOR = 11
    K_TO = 12
    K_STEP = 13
    K_NEXT = 14
    K_WHILE = 15
    K_READLN = 16
    K_WRITELN = 17

    # Limiters
    LIM_NE = 18
    LIM_EQ = 19
    LIM_LT = 20
    LIM_LTE = 21
    LIM_GT = 22
    LIM_GTE = 23
    LIM_PLUS = 24
    LIM_MINUS = 25
    LIM_OR = 26
    LIM_MUL = 27
    LIM_DIV = 28
    LIM_AND = 29
    LIM_COMMA = 30
    LIM_NOT = 31
    LIM_SEMICOLON = 32
    LIM_OPEN_PAREN = 33
    LIM_CLOSE_PAREN = 34
    LIM_OPEN_BRACKET = 35
    LIM_CLOSE_BRACKET = 36
    LIM_OPEN_CURLY = 37
    LIM_CLOSE_CURLY = 38
    LIM_ASSIGN = 39

    # Numeric literals
    NUMBER = 40

    # Identifiers
    IDENTIFIER = 41


# Lexeme table type enum (first number of lexeme, number of table)
class LexemeTableType(Enum):
    KEYWORDS = 1
    LIMITERS = 2
    NUMBERS = 3
    IDENTIFIERS = 4


# Class, representing lexeme
@dataclass
class Lexeme:
    lexeme_value: str           # String value of lexeme
    lexeme_type: LexemeType     # Lexeme type
    lexeme_pointer: int | None  # Pointer of lexeme in original program text
