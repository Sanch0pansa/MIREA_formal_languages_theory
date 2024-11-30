from course_work.core.models.AbstractSyntaxTree import ASTException
from course_work.core.parsers.SyntaxAnalyzer import SyntaxException


def handle_error(e: ASTException | SyntaxException, original_text: str):
    """
    Beautify error

    :param e: ASTException of SyntaxException
    :param original_text: original text of program
    :return: text or error
    """
    lexeme = e.lexeme
    position = lexeme.lexeme_pointer

    start_pos = position
    end_pos = position

    while original_text[start_pos] != "\n" and start_pos > 0:
        start_pos -= 1

    while original_text[end_pos] != "\n" and end_pos < len(original_text) - 1:
        end_pos += 1

    line = original_text[start_pos:end_pos + 1]
    line = line.strip("\n")

    ind = original_text.split("\n").index(line) + 1

    return (
        "Ошибка:\n" +
        f"{ind}: " + line + "\n"
        + " " * len(f"{ind}: ") + " " * (position - start_pos) + "^" * len(lexeme.lexeme_value) + "\nОписание: " + e.message
    )