import re
from typing import Generator


class FiniteStateMachineException(Exception):
    def __init__(self, message: str, pointer: int = 0, *args):
        self.pointer = pointer
        self.message = message
        super().__init__(self.message, *args)


class FiniteStateMachine:
    def __init__(self,
                 states: dict[str, dict[str, list[str | bool | None]]],
                 symbol_generator: Generator[str, None, None],
                 initial_state: str = "IN",
                 ):
        """
        Initialize finite state machine

        :param states: states dictionary {state: {regexp: [next_state, functions, move_pointer, error_text]}}
        :param initial_state: string of initial state
        """
        self.state = initial_state
        self.accumulator = ""
        self.pointer = 0
        self.finished = False
        self.states = states
        self.symbol_generator = symbol_generator
        self.current_symbol = next(self.symbol_generator)

    def handle_symbol(self):
        """
        Handle a provided symbol
        """

        # Searching corresponding regexp
        for state_regexp in self.states[self.state]:
            if re.fullmatch(state_regexp, self.current_symbol):
                res = self.states[self.state][state_regexp]
                self.handle_res(res)
                break

    def handle_res(self, res: list[str | bool | None]):
        """
        Handling action

        :param res: actions list
        """
        # Calling all functions
        for f in res[1].split(","):
            getattr(self, f)(*res[3:])

        # Going to next state
        self.state = res[0]

        # If move pointer is true, doing it
        if res[2]:
            self.pointer += 1
            self.current_symbol = next(self.symbol_generator)

        # Checking end state
        if self.state == "END":
            self.handle_finish()
            self.finished = True

    def handle_finish(self):
        """
        Handle a finish
        """
        pass

    def no_command(self, *args):
        """
        Handle no command
        """
        pass

    def acc(self):
        """
        Add char to accumulator
        """
        self.accumulator += self.current_symbol

    def error(self, error: str):
        """
        Handle error

        :param error: error string
        """

        compiled_error_message = error.replace(
            "$s", self.current_symbol
        ).replace(
            "$acc", self.accumulator
        )

        raise FiniteStateMachineException(
            compiled_error_message,
            pointer=self.pointer,
        )

    def make_step(self):
        """
        Make one step and handle one symbol
        """
        if not self.finished:
            self.handle_symbol()
