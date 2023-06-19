from typing import Callable, Generic, TypeVar
from AST import *

S = TypeVar("S")
T = TypeVar("T")


class NFA(Generic[S]):
    def __init__(self, alphabet: set, states: set[S], start_state: int, final_states: set[S], delta: dict) -> None:
        self.alphabet = alphabet
        self.states = states
        self.start_state = start_state
        self.final_states = final_states
        self.delta = delta

    def map(self, f: Callable[[S], T]) -> 'NFA[T]':
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

            new_v = set()
            for state in v:
                new_v.add(f(state))

            new_delta[new_k] = new_v

        return NFA(new_alphabet, new_states, new_start_state, new_final_states, new_delta)

    def next(self, from_state: S, on_chr: str) -> 'set[S]':
        next_states = set()
        for items in self.delta.items():
            key, value = items
            state, symbol = key
            if state == from_state and symbol == on_chr:
                next_states.update(value)
        return self.epsilon_closure(next_states)

    def getStates(self) -> 'set[S]':
        return self.states

    def epsilon_closure(self, states: 'set[S]') -> 'set[S]':
        stack = list(states)
        epsilon_closure_states = set(states)

        while stack:
            next_state = stack.pop()

            if (next_state, 'eps') in self.delta:
                for epsilon_transition_state in self.delta[(next_state, 'eps')]:
                    if epsilon_transition_state not in epsilon_closure_states:
                        stack.append(epsilon_transition_state)
                        epsilon_closure_states.add(epsilon_transition_state)

        return epsilon_closure_states

    def accepts(self, string: str) -> bool:
        if self.isFinal(self.start_state):
            return True

        current_states = self.epsilon_closure({self.start_state})

        for ch in string:
            next_states = set()
            for state in current_states:
                next_states.update(self.delta.get((state, ch), set()))

            current_states = self.epsilon_closure(next_states)

        return any(state in self.final_states for state in current_states)

    def isFinal(self, state: S) -> bool:
        return {state}.issubset(self.final_states)

    @staticmethod
    def fromPrenex(str: str) -> 'NFA[int]':
        ast = construct_ast(str)
        nfa = convert_ast_to_nfa(ast)
        return nfa


def post_order_ast(root, stack, operators):
    if root:
        post_order_ast(root.left, stack, operators)
        post_order_ast(root.right, stack, operators)

        if root.data in operators:
            first_nfa = stack.pop()
            if root.data in ["CONCAT", "UNION"]:
                second_nfa = stack.pop()
            else:
                second_nfa = None

            if root.data == "CONCAT":
                concat_nfa = concatenation(first_nfa, second_nfa)
                stack.append(concat_nfa)
            elif root.data == "UNION":
                union_nfa = union(second_nfa, first_nfa)
                stack.append(union_nfa)
            elif root.data == "STAR":
                star_nfa = star(first_nfa)
                stack.append(star_nfa)
            elif root.data == "MAYBE":
                maybe_nfa = maybe(first_nfa)
                stack.append(maybe_nfa)
            elif root.data == "PLUS":
                plus_nfa = plus(first_nfa)
                stack.append(plus_nfa)

        elif isinstance(root.data, str):
            if root.data == "eps":
                epsilon_nfa = eps_nfa()
                stack.append(epsilon_nfa)
            else:
                character_nfa = get_nfa_from_character(root.data)
                stack.append(character_nfa)


def convert_ast_to_nfa(root):
    stack = []
    operators = ["STAR", "CONCAT", "UNION", "MAYBE", "PLUS"]

    post_order_ast(root, stack, operators)
    return stack.pop()


states_index = 0


def get_next_state():
    global states_index
    states_index += 1
    return states_index


def concatenation(first_nfa, second_nfa):
    alphabet = first_nfa.alphabet.union(second_nfa.alphabet)
    eps = "eps"
    alphabet.add(eps)

    states = first_nfa.states.union(second_nfa.states)

    final_states = set()
    final_state = second_nfa.final_states.pop()
    final_states.add(final_state)

    start_state = first_nfa.start_state

    delta = {**first_nfa.delta, **second_nfa.delta}
    first_nfa_final_state = first_nfa.final_states.pop()

    delta[first_nfa_final_state, eps] = {second_nfa.start_state}

    nfa = NFA(alphabet, states, start_state, final_states, delta)
    return nfa


def union(first_nfa, second_nfa):
    alphabet = first_nfa.alphabet.union(second_nfa.alphabet)
    eps = "eps"
    alphabet.add(eps)

    states = first_nfa.states.union(second_nfa.states)
    final_states = set()

    start_state = get_next_state()
    final_state = get_next_state()
    states.update({start_state, final_state})
    final_states.add(final_state)

    delta = {**first_nfa.delta, **second_nfa.delta}

    first_final_state = first_nfa.final_states.pop()
    second_final_state = second_nfa.final_states.pop()

    delta[(first_final_state, eps)] = {final_state}
    delta[(second_final_state, eps)] = {final_state}
    delta[(start_state, eps)] = {first_nfa.start_state, second_nfa.start_state}

    return NFA(alphabet, states, start_state, final_states, delta)


def star(nfa):
    alphabet = nfa.alphabet
    eps = "eps"
    alphabet.add(eps)

    states = nfa.states

    start_state = get_next_state()
    states.add(start_state)

    final_state = get_next_state()
    states.add(final_state)
    final_states = set()
    final_states.add(final_state)

    delta = nfa.delta

    first_final = nfa.final_states.pop()
    first_key = (first_final, eps)

    if first_key not in delta.keys():
        delta[first_key] = set()

    delta[first_key].add(final_state)
    delta[first_key].add(nfa.start_state)

    second_key = (start_state, eps)
    delta[second_key] = set()
    delta[second_key].add(nfa.start_state)
    delta[second_key].add(final_state)

    return NFA(alphabet, states, start_state, final_states, delta)


def get_nfa_from_character(character):
    alphabet = set()
    alphabet.add(character)
    states = set()
    final_states = set()
    delta = {}

    start_state = get_next_state()
    states.add(start_state)

    final_state = get_next_state()
    states.add(final_state)
    final_states.add(final_state)

    key = (start_state, character)
    delta[key] = set()
    delta[key].add(final_state)

    nfa = NFA(alphabet, states, start_state, final_states, delta)
    return nfa


def plus(nfa):
    star_nfa = star(nfa)
    plus_nfa = concatenation(nfa, star_nfa)
    return plus_nfa


def maybe(nfa):
    maybe_nfa = nfa
    key = nfa.start_state, "eps"
    maybe_nfa.delta[key] = nfa.final_states

    return maybe_nfa


def eps_nfa():
    alphabet = set()
    states = set()
    final_states = set()

    start_state = get_next_state()
    final_states.add(start_state)
    states.add(start_state)
    delta = {(start_state, "eps"): start_state}

    return NFA(alphabet, states, start_state, final_states, delta)
