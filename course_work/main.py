from course_work.core.models.AbstractSyntaxTree2 import ASTException
from course_work.core.parsers.LexicalAnalyzer import LexicalAnalyzer
from course_work.core.parsers.SyntaxAnalyzer import SyntaxAnalyzer, SyntaxException
import json

from course_work.utils.errors_handler import handle_error


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


lexical_table = {
    "keywords": ["true", "false", "program", "var", "end", "begin", "int", "float", "bool", "if", "else", "for", "to",
                 "step", "next", "while", "readln", "writeln"],
    "limiters": ["!=", "==", "<", "<=", ">", ">=", "+", "-", "||", "*", "/", "&&", ",", "!", ";", "(", ")", "[", "]", "{", "}", ":="],
    "numbers": [],
    "identifiers": [],
}


if __name__ == "__main__":

    with open("./program.txt") as f:
        original_text = f.read()
        text = original_text.replace("\n", " ") + " "

    with open("./lexical_analyzer/states.json") as f:
        states = json.load(f)

    m = LexicalAnalyzer(
        text,
        states,
        lexical_table
    )

    m.run()

    with open("./lexical_analyzer/lexical_chain1.json", "w") as f:
        json.dump(m.lexical_chain.chain, f, indent=4)

    p = SyntaxAnalyzer(
        m.lexical_table,
        m.lexical_chain,
    )

    try:
        p.parse()
        p.AST.root.semantic_check()
        print("Программа корректна. Абстрактное синтаксическое дерево программы:")
        print(p.AST.root.to_string())
    except SyntaxException as e:
        print(handle_error(e, original_text))
    except ASTException as e:
        print(handle_error(e, original_text))