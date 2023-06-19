from typing import Tuple, List, Dict, Union

from Parser import *
from NFA import NFA
from DFA import convert_nfa_to_dfa


class Lexer:

    """
        This constructor initializes the lexer with a configuration
        The configuration is passed as a dictionary TOKEN -> REGEX

        You are encouraged to use the functions from the past stages to parse the regexes
    """

    def construct_nfa(self, nfas: List['NFA[S]']) -> 'NFA[S]':
        start_state = 0
        states = {start_state}
        final_states = set()
        delta = {}
        alphabet = set()

        for nfa in nfas:
            alphabet.update(nfa.alphabet)
            states.update(nfa.states)
            final_states.update(nfa.final_states)
            delta.update(nfa.delta)

        delta[(start_state, "eps")] = set()

        for nfa in nfas:
            delta[(start_state, "eps")].add(nfa.start_state)

        common_nfa = NFA(alphabet, states, start_state, final_states, delta)
        return common_nfa

    def __init__(self, configurations: Dict[str, str]) -> None:
        self.configurations = configurations

        self.dict_configuration_nfa = {}
        self.nfas = []

        for key, value in self.configurations.items():
            value = Parser.toPrenex(value)
            nfa = NFA.fromPrenex(value)

            self.nfas.append(nfa)
            self.dict_configuration_nfa[nfa] = key

        self.nfa = self.construct_nfa(self.nfas)
        self.dfa = convert_nfa_to_dfa(self.nfa)

    """
        The main functionality of the lexer, receives a word and lexes it
        according to the provided configuration.

        The return value is either a List of tuples (TOKEN, LEXEM) if the lexer succedes
        or a string message if the lexer fails
    """

    def lex(self, word: str) -> Union[List[Tuple[str, str]], str]:
        state = self.dfa.start_state
        token = ""
        output = []

        i = 0
        start_of_new_token = 0
        end_of_new_token = 0
        line = 0
        new_line_indexes = set()
        while i < len(word) + 1:
            state = self.dfa.next(state, word[i])

            if word[i] == '\n' and i not in new_line_indexes:
                line += 1
                new_line_indexes.add(i)

            i += 1
            if self.dfa.isFinal(state):
                end_of_new_token = i
                token = word[start_of_new_token: end_of_new_token]

            if self.dfa.is_sink_state(state):
                state = self.dfa.start_state

                if token == "":
                    error_msg = "No viable alternative at character " + str(i - 1) + ", line " + str(line)
                    return error_msg

                for nfa in self.nfas:
                    if nfa.accepts(token):

                        output.append((self.dict_configuration_nfa[nfa], token))
                        token = ""
                        i = end_of_new_token
                        start_of_new_token = i
                        break

            if i == len(word) and token:
                for nfa in self.nfas:
                    if nfa.accepts(token):
                        output.append((self.dict_configuration_nfa[nfa], token))
                        token = ""
                        i = end_of_new_token
                        start_of_new_token = i
                        state = self.dfa.start_state

            if i == len(word):
                if end_of_new_token != len(word):
                    error_msg = "No viable alternative at character EOF, line " + str(line)
                    return error_msg
                break

        keys_to_remove = ['SPACE_PR', 'NEW_LINE_PR', 'TAB_PR']
        output = [item for item in output if item[0] not in keys_to_remove]

        return output
