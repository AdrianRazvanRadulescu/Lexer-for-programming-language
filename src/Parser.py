from __future__ import annotations

from AST import *


def convert_compact_form(alphabet):
    compact_form = list()
    compact_form.append(Operator("("))
    for i in range(len(alphabet)):
        compact_form.append(Character(alphabet[i]))
        compact_form.append(Operator("|"))
    compact_form[len(compact_form) - 1] = Operator(")")
    return compact_form


class Parser:

    @staticmethod
    def convert_question(expr):
        question_operator = Operator('?')

        i = 0
        while i < len(expr) - 1:
            if expr[i + 1] == question_operator:

                if expr[i] == Operator(')'):
                    applied_star_expr = []

                    j = i
                    number_of_closed = 1
                    number_of_open = 0

                    while j > -1:

                        if number_of_open == number_of_closed:
                            break

                        applied_star_expr.append(expr[j])

                        if expr[j] == Operator('('):
                            number_of_open += 1

                        if j < i and expr[j] == Operator(')'):
                            number_of_closed += 1

                        j -= 1

                    applied_star_expr.reverse()

                    repl_expr = list()
                    repl_expr.append(Operator('('))
                    repl_expr.extend(applied_star_expr)
                    repl_expr.append(Operator('|'))
                    repl_expr.append(Character('&'))

                    repl_expr.append(Operator(')'))

                    expr[j + 1: i + 2] = repl_expr
                    i = j + len(repl_expr) + 4

                elif i < len(expr) - 1 and type(expr[i]) == Character:
                    repl_expr = list()
                    repl_expr.append(Operator('('))
                    repl_expr.append(expr[i])

                    repl_expr.append(Operator('|'))
                    repl_expr.append(Character('&'))

                    repl_expr.append(Operator(')'))

                    expr[i: i + 2] = repl_expr
                    i += len(repl_expr)
            i += 1

        return expr

    @staticmethod
    def convert_plus(expr):
        plus_operator = Operator('+')
        i = 0
        while i < len(expr) - 1:
            if expr[i + 1] == plus_operator:

                if expr[i] == Operator(')'):
                    applied_star_expr = []

                    j = i
                    number_of_closed = 1
                    number_of_open = 0

                    while j > -1:

                        if number_of_open == number_of_closed:
                            break

                        applied_star_expr.append(expr[j])

                        if expr[j] == Operator('('):
                            number_of_open += 1
                            continue

                        if j < i and expr[j] == Operator(')'):
                            number_of_closed += 1

                        j -= 1

                    applied_star_expr.reverse()

                    repl_expr = list()
                    repl_expr.append(Operator('('))
                    repl_expr.extend(applied_star_expr)
                    repl_expr.extend(applied_star_expr)

                    repl_expr.append(Operator('*'))
                    repl_expr.append(Operator(')'))

                    expr[j: i + 2] = repl_expr

                    i = j + len(repl_expr) + 2

                if i < len(expr) - 1 and type(expr[i]) == Character:
                    repl_expr = list()
                    repl_expr.append(Operator('('))
                    repl_expr.append(expr[i])
                    repl_expr.append(expr[i])
                    repl_expr.append(Operator('*'))
                    repl_expr.append(Operator(')'))

                    expr[i: i + 2] = repl_expr
                    i += len(repl_expr)
            i += 1

        return expr

    @staticmethod
    def preprocess(regex: str) -> list:
        regex = regex.replace("eps", '&')

        processed = []
        operators = "()*|?+"
        ranges = {
            "[0-9]": "0123456789",
            "[a-z]": "abcdefghijklmnopqrstuvwxyz",
            "[A-Z]": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        }

        i = 0
        while i < len(regex):

            if regex[i: i + 5] in ranges:
                alphabet = ranges[regex[i: i + 5]]
                processed += convert_compact_form(alphabet)
                i += 5
                continue

            if i + 1 < len(regex) and i > 0 and regex[i - 1] == "'" and regex[i + 1] == "'":
                char_quoted = "'" + regex[i] + "'"
                processed.append(Character(char_quoted))
                i += 1
                continue

            if regex[i] == "'":
                i += 1
                continue

            if regex[i] in operators:
                processed.append(Operator(regex[i]))
                i += 1
                continue

            processed.append(Character(regex[i]))
            i += 1

        op_question = Operator('?')
        op_plus = Operator('+')

        if op_plus in processed:
            processed = Parser.convert_plus(processed)

        if op_question in processed:
            processed = Parser.convert_question(processed)

        return processed

    @staticmethod
    def toPrenex(s: str) -> str:
        s = s.replace("eps", '&')
        preprocessed_regex = Parser.preprocess(s)

        if len(preprocessed_regex) == 1:
            prefix_expression = preprocessed_regex[0].chr
            prefix_expression = prefix_expression.replace('&', "eps")
            return prefix_expression

        ast = convert_expression_to_ast(preprocessed_regex)[0]
        prefix_expression = ast.to_string()
        prefix_expression = prefix_expression.replace('&', "eps")
        return prefix_expression
