import os.path
import json
from http.client import HTTPException

from course_work.common.lexemes import Lexeme, LexemeType, LexemeTableType

"""
<операции_группы_отношения>:: = != | == | < | <= | > | >=
<операции_группы_сложения>:: = + | - | ||
<операции_группы_умножения>:: = * | / | &&
<унарная_операция>::= !
<выражение>::= <операнд>{<операции_группы_отношения> <операнд>}
<операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>}
<слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
<множитель>::= <идентификатор> | <число> | <логическая_константа> | <унарная_операция> <множитель> | «(»<выражение>«)»
<число>::= <целое> | <действительное>
<логическая_константа>::= true | false
<идентификатор>::= <буква> {<буква> | <цифра>}
<буква>::= A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P | Q | R | S | T | U | V | W | X | Y | Z | a | b | c | d | e | f | g | h | i | j | k | l | m | n | o | p | q | r | s | t | u | v | w | x | y | z
<цифра>::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
<целое>::= <двоичное> | <восьмеричное> | <десятичное> | <шестнадцатеричное>
<двоичное>::= {/ 0 | 1 /} (B | b)
<восьмеричное>::= {/ 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 /} (O | o)
<десятичное>::= {/ <цифра> /} [D | d]
<шестнадцатеричное>::= <цифра> {<цифра> | A | B | C | D | E | F | a | b | c | d | e | f} (H | h)
<действительное>::= <числовая_строка> <порядок> | [<числовая_строка>] . <числовая_строка> [порядок]
<числовая_строка>::= {/ <цифра> /} 
<порядок>::= ( E | e )[+ | -] <числовая_строка>
<программа>::= program var <описание> begin <оператор> {; <оператор>} end.
<описание>::= <тип> <идентификатор> { , <идентификатор> }
<тип>::= int | float | bool
<оператор>::= <составной> | <присваивания> | <условный> | <фиксированного_цикла> | <условного_цикла> | <ввода> | <вывода>
<составной>::= begin <оператор> { ; <оператор> } end
<присваивания>::= <идентификатор> := <выражение>
<условный>::= if «(»<выражение> «)» <оператор> [else <оператор>]
<фиксированного_цикла>::= for <присваивания> to <выражение> [step <выражение>] <оператор> next
<условного_цикла>::= while «(»<выражение> «)» <оператор>
<ввода>::= readln идентификатор {, <идентификатор> }
<вывода>::= writeln <выражение> {, <выражение> } 
комменты - { }
"""


def read_lexical_table_from_json(path_to_file: str) -> dict[str, list[str]]:
    """
    Read lexical table form file

    :param path_to_file: path to file with saved lexical table
    :return: dict with 4 keys: keywords, limiters, numbers, identifiers
    """
    # Check if file does not exist
    if not os.path.exists(path_to_file):
        raise Exception("Lexical table file does not exist")

    # Read file
    with open(path_to_file, 'r') as file:
        data = json.load(file)

        return data


def read_lexical_chain_from_json(path_to_file: str) -> list[tuple[int, int]]:
    """
    Read lexical chain from file

    :param path_to_file: path to file with saved lexical chain
    :return: list of lexeme tuples
    """
    # Check if file does not exist
    if not os.path.exists(path_to_file):
        raise Exception("Lexical chain file does not exist")

    # Read file
    with open(path_to_file, 'r') as file:
        data = json.load(file)

        return [(x[0] - 1, x[1]) for x in data]


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

    def get_lexeme_type(self, lexeme_tuple: tuple[int, int]) -> LexemeType:
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

    def get_lexeme_value(self, lexeme_tuple: tuple[int, int]) -> str:
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


# Class of lexical chain
class LexicalChain:
    def __init__(self, chain: list[tuple[int, int]], lexical_table: LexicalTable):
        """
        Initialize lexical chain

        :param chain: lexical chain presented as list of lexemes, presented as tuple
        """
        self.chain = chain                  # Chain presented as list
        self.lexical_table = lexical_table  # Object of LexicalTable

        self.pointer = 0                    # Pointer of current lexeme

    def next_lexeme(self) -> Lexeme:
        """
        Get next lexeme in chain

        :return: next Lexeme
        """
        lexeme_tuple: tuple[int, int] = self.chain[self.pointer]
        lexeme: Lexeme = Lexeme(
            lexeme_type=self.lexical_table.get_lexeme_type(lexeme_tuple),
            lexeme_value=self.lexical_table.get_lexeme_value(lexeme_tuple)
        )
        self.pointer += 1
        return lexeme


# Syntax parser
class SyntaxParser:
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

    # Recursive functions
    def func_program(self):
        if self.check_current_lexeme(LexemeType.K_PROGRAM):
            self.read_next_lexeme()
        else:
            raise Exception("Incorrect program start")
        if self.check_current_lexeme(LexemeType.K_VAR):
            self.read_next_lexeme()
        else:
            raise Exception("Incorrect program var start")
        self.func_description()

        if self.check_current_lexeme(LexemeType.K_BEGIN):
            self.read_next_lexeme()
        else:
            raise Exception("Incorrect program begin")

        self.func_operator()
        while self.check_current_lexeme(LexemeType.LIM_SEMICOLON):
            self.read_next_lexeme()
            self.func_operator()

        if self.check_current_lexeme(LexemeType.K_END):
            pass
        else:
            raise Exception("Incorrect program end")

    def func_description(self):
        if self.check_current_lexeme(LexemeType.K_INT, LexemeType.K_FLOAT, LexemeType.K_BOOL):
            self.read_next_lexeme()
        else:
            raise Exception(f"Incorrect program description, {self.current_lexeme.lexeme_value}")

        if self.check_current_lexeme(LexemeType.IDENTIFIER):
            self.read_next_lexeme()
        else:
            raise Exception("Incorrect type declaration")

        while self.check_current_lexeme(LexemeType.LIM_COMMA):
            self.read_next_lexeme()
            if self.check_current_lexeme(LexemeType.IDENTIFIER):
                self.read_next_lexeme()
            else:
                raise Exception("Incorrect type declaration")

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
            raise Exception("Incorrect operator syntax")

    def func_composite_operator(self):
        pass

    def func_assignment_operator(self):
        pass

    def func_condition_operator(self):
        pass

    def func_fixed_loop_operator(self):
        pass

    def func_conditional_loop_operator(self):
        pass

    def func_read(self):
        pass

    def func_write(self):
        pass

    def func_expression(self):
        pass

    def func_operand(self):
        pass

    def func_term(self):
        pass

    def func_factor(self):
        pass



    # Main parsing entrypoint
    def parse(self):
        self.read_next_lexeme()
        self.func_program()


if __name__ == "__main__":
    lt = LexicalTable(
        read_lexical_table_from_json("../lexical_analyzer/lexical_table.json")
    )

    lc = LexicalChain(
        read_lexical_chain_from_json("../lexical_analyzer/lexical_chain.json"),
        lt,
    )

    p = SyntaxParser(
        lt,
        lc,
    )

    p.parse()