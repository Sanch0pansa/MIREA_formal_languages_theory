from course_work.core.models.AbstractSyntaxTree import ASTException
from course_work.core.parsers.LexicalAnalyzer import LexicalAnalyzer
from course_work.core.parsers.SyntaxAnalyzer import SyntaxAnalyzer, SyntaxException
import json

from course_work.utils.errors_handler import handle_error

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
        print(p.AST.root.to_string())
    except SyntaxException as e:
        print(handle_error(e, original_text))
    except ASTException as e:
        print(handle_error(e, original_text))