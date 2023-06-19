from Regex import *

import shlex


class MyAST:
    def __init__(self, left=None, right=None, data=None):
        self.left = left
        self.right = right
        self.data = data

    def to_string(self):
        if self.data is None:
            return ""

        left_str = self.left.to_string() if self.left else ""
        right_str = self.right.to_string() if self.right else ""

        if type(self.data) == Operator:
            if self.data.op == ".":
                return f"CONCAT {left_str} {right_str}"
            elif self.data.op == "*":
                return f"STAR {left_str}"
            elif self.data.op == "|":
                return f"UNION {left_str} {right_str}"
        elif type(self.data) == Character:
            if self.data.chr == "&":
                return "eps"
            else:
                return self.data.chr


def replace_triple_quotes(string):
    return string.replace("'''", "&")


def split_expression(expression):
    expression = replace_triple_quotes(expression)
    shlex_list = shlex.split(expression)

    expression_list = ["'" if x == "&" else x for x in shlex_list]

    return expression_list


def construct_ast(expression):

    list_expression = split_expression(expression)

    operators = ["CONCAT", "UNION", "STAR", "PLUS", "MAYBE"]
    binary_operators = ["CONCAT", "UNION"]
    unary_operators = ["STAR", "PLUS", "MAYBE"]

    list_expression.reverse()
    nodes = []
    for i in range(len(list_expression)):
        if list_expression[i] not in operators:
            new_node = MyAST()
            new_node.data = list_expression[i]
            new_node.left = None
            new_node.right = None

            nodes.append(new_node)
        else:
            right = nodes.pop()

            if list_expression[i] in binary_operators:
                left = nodes.pop()
                new_node = MyAST()
                new_node.left = left
                new_node.right = right
                new_node.data = list_expression[i]
                nodes.append(new_node)

            elif list_expression[i] in unary_operators:
                left = None
                new_node = MyAST()
                new_node.left = left
                new_node.right = right
                new_node.data = list_expression[i]
                nodes.append(new_node)

    return nodes.pop()


def convert_concat(expr):
    i = 0
    concat_operation = Operator('.')

    while i < len(expr) - 1:
        if type(expr[i]) != Operator and type(expr[i + 1]) != Operator:
            ast = MyAST()
            ast.data = concat_operation

            if type(expr[i]) == MyAST:
                ast.left = expr[i]
            elif type(expr[i]) == Character:
                ast.left = MyAST()
                ast.left.data = expr[i]

            if type(expr[i + 1]) == MyAST:
                ast.right = expr[i + 1]
            elif type(expr[i + 1]) == Character:
                ast.right = MyAST()
                ast.right.data = expr[i + 1]

            expr[i: i + 2] = [ast]
            i -= 1
        i += 1

    return expr


def convert_star(expr):
    i = 0
    star_operation = Operator('*')
    while i < len(expr) - 1:
        if expr[i + 1] == star_operation:
            ast = MyAST()
            ast.data = star_operation
            if isinstance(expr[i], MyAST):
                ast.left = expr[i]
            else:
                ast.left = MyAST(data=expr[i])
            ast.right = None
            expr[i: i + 2] = [ast]
            i -= 1
        i += 1
    return expr


def convert_union(expr):
    i = 0
    union_operation = Operator('|')

    while i < len(expr) - 2:
        if expr[i + 1] == union_operation:
            if type(expr[i]) != Operator and type(expr[i + 2]) != Operator:
                ast = MyAST()
                ast.data = union_operation
                ast.left = expr[i] if type(expr[i]) == MyAST else MyAST(data=expr[i])
                ast.right = expr[i + 2] if type(expr[i + 2]) == MyAST else MyAST(data=expr[i + 2])
                expr[i: i + 3] = [ast]
                i -= 1
        i += 1

    return expr


def convert_expression_to_ast(processed_expr):
    open_operation = Operator('(')
    closed_operation = Operator(')')
    i = 0

    while i < len(processed_expr) - 2:
        if processed_expr[i] == open_operation and processed_expr[i + 2] == closed_operation:
            processed_expr.pop(i + 2)
            processed_expr.pop(i)

        i += 1

    i = 0
    while i < len(processed_expr):

        if processed_expr[i] == open_operation:
            number_of_open = 1
            number_of_closed = 0

            j = i + 1

            while j < len(processed_expr):
                if processed_expr[j] == closed_operation:
                    number_of_closed += 1

                if processed_expr[j] == open_operation:
                    number_of_open += 1

                if number_of_open == number_of_closed:
                    break

                j = j + 1

            converted = convert_expression_to_ast(processed_expr[i + 1: j])
            processed_expr[i: j + 1] = converted
            i -= 1

        i += 1

    check_sub_expr = 0

    for i in range(len(processed_expr)):
        if processed_expr[i] == open_operation or processed_expr[i] == closed_operation:
            check_sub_expr = 1

    if check_sub_expr == 0:
        processed_expr = convert_star(processed_expr)
        processed_expr = convert_concat(processed_expr)
        processed_expr = convert_union(processed_expr)

        return processed_expr
