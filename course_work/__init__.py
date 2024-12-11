import click
import json
from course_work.core.models.AbstractSyntaxTree2 import ASTException
from course_work.core.models.FiniteStateMachine import FiniteStateMachineException
from course_work.core.parsers.LexicalAnalyzer import LexicalAnalyzer, LexemeIterator
from course_work.core.parsers.SyntaxAnalyzer import SyntaxAnalyzer, SyntaxException
from course_work.utils.errors_handler import handle_error

# Path to state file
STATES_JSON_PATH = "./course_work/states.json"

lexical_table = {
    "keywords": ["true", "false", "program", "var", "end", "begin", "int", "float", "bool", "if", "else", "for", "to",
                 "step", "next", "while", "readln", "writeln"],
    "limiters": ["!=", "==", "<", "<=", ">", ">=", "+", "-", "||", "*", "/", "&&", ",", "!", ";", "(", ")", "[", "]", "{", "}", ":=", "@"],
    "numbers": [],
    "identifiers": [],
}

def read_string(string):
    """
    Generator to read string symbol by symbol

    :param string: string to iterate
    """
    for c in string:
        yield c
    yield "@"

@click.command()
@click.argument('file_path', type=click.Path(exists=True, readable=True))
def analyze(file_path):
    """
    Code analyzer

    :param file_path: Path to file to analyze
    """

    # Reading code
    with open(file_path, encoding='utf-8') as f:
        original_text = f.read()
        text = original_text.replace("\n", " ") + " "

    # Reading states for state machine
    try:
        with open(STATES_JSON_PATH, encoding="utf-8") as f:
            states = json.load(f)
    except FileNotFoundError:
        click.echo(f"Ошибка: файл {STATES_JSON_PATH} не найден.")
        return
    except json.JSONDecodeError as e:
        click.echo(f"Ошибка чтения JSON файла {STATES_JSON_PATH}: {e}")
        return

    # Initializing analyzers
    lexer = LexicalAnalyzer(states, lexical_table, read_string(text))
    lex_iterator = LexemeIterator(lexer)
    p = SyntaxAnalyzer(lexer.lexical_table, lex_iterator)

    # Making analyze
    try:
        p.parse()
        p.AST.root.semantic_check()
        click.echo("Программа корректна. Абстрактное синтаксическое дерево программы:")
        click.echo(p.AST.root.to_string())
    except SyntaxException as e:
        click.echo("Возникла синтаксическая ошибка!")
        click.echo(handle_error(e, original_text))
    except ASTException as e:
        click.echo("Возникла семантическая ошибка!")
        click.echo(handle_error(e, original_text))
    except FiniteStateMachineException as e:
        click.echo("Возникла лексическая ошибка!")
        click.echo(e.message)

if __name__ == "__main__":
    analyze()
