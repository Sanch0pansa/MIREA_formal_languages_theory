import json
import re

"""
Вариант: 213321

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

with open("program.txt") as f:
    text = f.read().replace("\n", " ") + " "

lexical_table = {
    "keywords": ["true", "false", "program", "var", "end", "begin", "int", "float", "bool", "if", "else", "for", "to",
                 "step", "next", "while", "readln", "writeln"],
    "limiters": ["!=", "==", "<", "<=", ">", ">=", "+", "-", "||", "*", "/", "&&", ",", "!", ";", "(", ")", "[", "]", "{", "}", ":="],
    "numbers": [],
    "identifiers": [],
}

class Lexer:
    def __init__(self, string):
        self.string = string
        self.state = "IN"
        self.accumulator = ""
        self.pointer = 0
        self.finished = False
        self.states = json.load(open("states.json", encoding="utf-8"))
        self.chain = []

    def handle_symbol(self):
        c = self.string[self.pointer]
        for state_regexp in self.states[self.state]:
            if re.fullmatch(state_regexp, c):
                res = self.states[self.state][state_regexp]
                self.handle_res(res)
                break

    def handle_res(self, res):
        for f in res[1].split(","):
            getattr(self, f)(*res[3:])
        self.state = res[0]
        if res[2]:
            self.pointer += 1
            if self.pointer == len(self.string):
                self.finished = True

    def no_command(self, *args):
        pass

    def acc(self):
        self.accumulator += self.string[self.pointer]

    def add_number(self):
        token = self.accumulator
        if token not in lexical_table['numbers']:
            lexical_table['numbers'].append(token)
        self.chain.append(
            (3, lexical_table['numbers'].index(token))
        )
        self.accumulator = ""

    def add_limiter(self):
        token = self.accumulator
        self.chain.append(
            (2, lexical_table['limiters'].index(token))
        )
        self.accumulator = ""

    def add_identifier(self):
        token = self.accumulator
        if token in lexical_table['keywords']:
            self.chain.append(
                (1, lexical_table['keywords'].index(token))
            )
        else:
            if token not in lexical_table['identifiers']:
                lexical_table['identifiers'].append(token)
            self.chain.append(
                (4, lexical_table['identifiers'].index(token))
            )
        self.accumulator = ""

    def error(self, error):
        print(self.accumulator)
        print(
            error.replace(
                "$s", self.string[self.pointer]
            ).replace(
                "$acc", self.accumulator
            )
        )
        self.finished = True


m = Lexer(text)
while not m.finished:
    m.handle_symbol()

with open("lexical_chain.json", "w") as f:
    f.write(
        json.dumps(m.chain, indent=4)
    )