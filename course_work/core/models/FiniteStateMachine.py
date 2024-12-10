import re


class FiniteStateMachineException(Exception):
    def __init__(self, message: str, pointer: int = 0, *args):
        self.pointer = pointer
        self.message = message
        super().__init__(self.message, *args)


class FiniteStateMachine:
    def __init__(self,
                 string: str,
                 states: dict[str, dict[str, list[str | bool | None]]],
                 initial_state: str = "IN",
                 ):
        """
        Initialize finite state machine

        :param string: string to analyze
        :param states: states dictionary {state: {regexp: [next_state, functions, move_pointer, error_text]}}
        :param initial_state: string of initial state
        """
        self.string = string
        self.state = initial_state
        self.accumulator = ""
        self.pointer = 0
        self.finished = False
        self.states = states

    def handle_symbol(self):
        """
        Handle a symbol by current pointer
        """
        # Reading char by pointer
        c = self.string[self.pointer]

        # Searching corresponding regexp
        for state_regexp in self.states[self.state]:
            if re.fullmatch(state_regexp, c):
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

            # Checking reaching end of string
            if self.pointer == len(self.string):
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
        self.accumulator += self.string[self.pointer]

    def error(self, error: str):
        """
        Handle error

        :param error: error string
        """

        compiled_error_message = error.replace(
            "$s", self.string[self.pointer]
        ).replace(
            "$acc", self.accumulator
        )

        raise FiniteStateMachineException(
            compiled_error_message,
            pointer=self.pointer,
        )

    def run(self):
        """
        Run finite state machine
        """
        while not self.finished:
            self.handle_symbol()
