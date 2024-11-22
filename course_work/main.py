from parser.main import (
    LexicalTable,
    LexicalChain,
    read_lexical_table_from_json,
    read_lexical_chain_from_json,
    SyntaxParser
)
import json
from lexical_analyzer.main import Lexer, lexical_table

if __name__ == "__main__":

    with open("./program.txt") as f:
        text = f.read().replace("\n", " ") + " "

    m = Lexer(text, "./lexical_analyzer/states.json")
    while not m.finished:
        m.handle_symbol()

    with open("./lexical_chain.json", "w") as f:
        f.write(
            json.dumps(m.chain, indent=4)
        )

    with open("./lexical_table.json", "w") as f:
        f.write(
            json.dumps(lexical_table, indent=4)
        )

    lt = LexicalTable(
        read_lexical_table_from_json("./lexical_table.json")
    )

    lc = LexicalChain(
        read_lexical_chain_from_json("./lexical_chain.json"),
        lt,
    )

    p = SyntaxParser(
        lt,
        lc,
    )

    p.parse()