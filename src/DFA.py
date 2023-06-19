from typing import Callable, Generic, TypeVar
from NFA import NFA
from copy import deepcopy

S = TypeVar("S")
T = TypeVar("T")


class DFA(Generic[S]):
    def __init__(self, alphabet: set, states: set[S], start_state: int, final_states: set[S], delta: dict) -> None:
        self.alphabet = alphabet
        self.states = states
        self.start_state = start_state
        self.final_states = final_states
        self.delta = delta

    def map(self, f: Callable[[S], T]) -> 'DFA[T]':

        new_alphabet = self.alphabet
        state_list = list(self.states)
        new_state_list = []

        for state in state_list:
            new_state_list.append(f(state))

        new_states = set(new_state_list)

        final_state_list = list(self.final_states)
        new_final_state_list = []

        for final_state in final_state_list:
            new_final_state_list.append(f(final_state))

        new_final_states = set(new_final_state_list)
        new_start_state = f(self.start_state)

        new_delta = {}
        for k, v in self.delta.items():
            state, symbol = k
            new_state = f(state)
            new_k = new_state, symbol
            new_v = f(v)
            new_delta[new_k] = new_v

        return DFA(new_alphabet, new_states, new_start_state, new_final_states, new_delta)

    def is_sink_state(self, state: S) -> bool:
        for symbol in self.alphabet:
            if self.next(state, symbol) != state:
                return False
        return True

    def next(self, from_state: S, on_chr: str) -> S:
        for items in self.delta.items():
            key, value = items
            state, symbol = key
            if state == from_state and symbol == on_chr:
                return value

    def getStates(self) -> 'set[S]':
        return self.states

    def accepts(self, str: str) -> bool:
        if str == "":
            if self.start_state in self.final_states:
                return True
            return False

        state = self.start_state

        for c in str:
            state = self.next(state, c)
        if state in self.final_states:
            return True
        return False

    def isFinal(self, state: S) -> bool:
        return {state}.issubset(self.final_states)

    @staticmethod
    def fromPrenex(str: str) -> 'DFA[int]':
        nfa_after_parsing = NFA.fromPrenex(str)
        dfa = convert_nfa_to_dfa(nfa_after_parsing)

        return dfa


def dfs(closure, nfa, node, eps):
    if node not in closure:
        closure.add(node)
        pair = node, eps
        if pair in nfa.delta:
            for neighbour in nfa.delta[pair]:
                dfs(closure, nfa, neighbour, eps)


def compute_closure(nfa, state):
    closure = set()
    eps = 'eps'
    dfs(closure, nfa, state, eps)

    return closure


def convert_nfa_to_dfa(nfa):
    if len(nfa.states) == 1:
        dfa = DFA(nfa.alphabet, nfa.states, nfa.start_state, nfa.final_states, nfa.delta)
        return dfa

    start_set = compute_closure(nfa, nfa.start_state)

    queue = set()
    queue.add(frozenset(start_set))

    dfa_states = queue.copy()
    dfa_delta = {}

    alphabet = nfa.alphabet

    dfa_final_states = set()

    while len(queue) > 0:
        current_state = queue.pop()

        for symbol in alphabet:
            if symbol == 'eps':
                continue

            next_dfa_state = set()
            for state_nfa in current_state:
                pair = state_nfa, symbol

                if pair in nfa.delta.keys():
                    next_dfa_state.update(nfa.delta[pair])

                    if "eps" in alphabet:
                        for x in nfa.delta[pair]:
                            next_dfa_state.update(compute_closure(nfa, x))

            next_dfa_state = frozenset(next_dfa_state)
            pair = current_state, symbol
            dfa_delta[pair] = next_dfa_state

            if next_dfa_state not in dfa_states:
                dfa_states.add(frozenset(next_dfa_state.copy()))
                queue.add(frozenset(next_dfa_state.copy()))

    for state in dfa_states:
        for x in state:
            if x in nfa.final_states:
                dfa_final_states.add(frozenset(state))

    dfa_states_f = set()

    final_states_f = set()
    start_set = frozenset(start_set)
    start = 0

    dict_list = []
    listPre = []
    pair = 0, 0
    y = 0

    for key, value in dfa_delta.items():
        temp = [key, value]
        dict_list.append(temp)
        temp = [pair, y]
        listPre.append(temp)

    index = 0

    for state in dfa_states:
        dfa_states_f.add(index)

        if state in dfa_final_states:
            final_states_f.add(index)

        for i in range(len(dict_list)):
            key, value = dict_list[i]
            if key[0] == start_set:
                temp = i

            if key[0] == state:
                key_final, pre_final = listPre[i]
                key_temp = index, key[1]

                listPre[i] = key_temp, pre_final

            if value == state:
                key_final, pre_final = listPre[i]
                pre_final = index
                listPre[i] = key_final, pre_final

        index += 1

    key, value = listPre[temp]
    x = deepcopy(key[0])
    y = 0

    if x != y:
        for i in range(len(listPre)):

            key, value = listPre[i]
            new_key = deepcopy(key)
            new_value = deepcopy(value)

            if key[0] == x:
                new_key = y, new_key[1]

            if key[0] == y:
                new_key = x, new_key[1]

            if value == x:
                new_value = y

            if value == y:
                new_value = x

            listPre[i] = new_key, new_value

        if x in final_states_f and y not in final_states_f:
            final_states_f.remove(x)
            final_states_f.add(y)

        elif y in final_states_f and x not in final_states_f:
            final_states_f.remove(y)
            final_states_f.add(x)

    alphabet.discard("eps")

    dfa_delta = {}

    for key, value in listPre:
        dfa_delta[key] = value

    dfa = DFA(alphabet, dfa_states_f, start, final_states_f, dfa_delta)

    return dfa
