'''
Calculator that runs in a loop and evaluates expressions given by the user
'''

import math
import numbers
import re
import sys
import numpy as np
from containers import Queue, Stack
from wrappers import Function, Operator


class Calculator():
    '''
    The calculator takes a string in the form of an equation, parses it into
    operators, operands, functions and parentheses. It then converts from infix
    to reverse polish notation and evaluates the expression.
    '''

    def __init__(self):
        self.functions = {
            'EXP': Function(np.exp),
            'LOG': Function(np.log),
            'SIN': Function(np.sin),
            'COS': Function(np.cos),
            'SQRT': Function(np.sqrt),
            'ABS': Function(np.abs)
        }

        self.constants = {
            'PI': math.pi,
            'TAU': math.tau,
            'E': math.e
        }

        self.operators = {
            '+': Operator(np.add, strength=0),
            '~': Operator(np.subtract, strength=0),
            '/': Operator(np.divide, strength=1),
            '*': Operator(np.multiply, strength=1),
        }

        self.output_queue = Queue()

    def calculate(self):
        '''
        Calculate the value of the RPN-equation stored in output_queue.
        '''
        stack = Stack()
        while not self.output_queue.is_empty():
            elem = self.output_queue.pop()

            if isinstance(elem, numbers.Number):
                stack.push(elem)

            if isinstance(elem, Function):
                _input = stack.pop()
                stack.push(elem.execute(_input))

            if isinstance(elem, Operator):
                _second = stack.pop()
                _first = stack.pop()
                stack.push(elem.execute(_first, _second))
        return stack.pop()

    def generate_output_queue(self, input_list):
        '''
        Converts a list of operators, functions, operands, constants and
        parentheses from infix notation to reverse polish notation using the
        shunting-yard algorithm
        '''
        def operator_precedence(top, elem):
            '''
            Function to determine wether to pop from op_stack
            '''
            precedence = False
            precedence |= isinstance(top, Function)
            if isinstance(top, Operator):
                precedence |= top.strength >= elem.strength
            precedence &= top != '('

            return precedence

        self.output_queue = Queue()
        op_stack = Stack()

        for elem in input_list:
            if isinstance(elem, numbers.Number):
                self.output_queue.push(elem)

            if isinstance(elem, Function):
                op_stack.push(elem)

            if isinstance(elem, Operator):
                if not op_stack.is_empty():
                    top = op_stack.peek()
                    while top is not None and operator_precedence(top, elem):
                        self.output_queue.push(op_stack.pop())
                        if not op_stack.is_empty():
                            top = op_stack.peek()
                        else:
                            top = None
                op_stack.push(elem)

            if elem == '(':
                op_stack.push(elem)

            if elem == ')':
                next_op = op_stack.pop()
                while next_op != '(':
                    self.output_queue.push(next_op)
                    next_op = op_stack.pop()

        while not op_stack.is_empty():
            elem = op_stack.pop()
            self.output_queue.push(elem)

    def parse_string_to_list(self, input_str):
        '''
        Parse input_str into a list of operators, operands, parentheses,
        constants and functions, using regular expressions. Then substitute the
        functions and operators found with their corresponding wrapper object.
        Strings in the form of positive or negative integers/floats are
        converted to float.
        '''

        float_re = r'-?\d+\.\d+'
        int_re = r'-?\d+'
        paren_re = r'\(|\)'
        operator_re = r'\+|\~|\*|/|'
        constants_re = '|'.join(self.constants.keys())
        fun_re = '|'.join(self.functions.keys())

        regex = '|'.join([float_re, int_re, paren_re,
                          operator_re, fun_re, constants_re])

        # re.findall preserves the order of the matches
        matches = re.findall(regex, input_str.upper())

        result = []
        for match in matches:
            # Function
            if match in self.functions.keys():
                result += [self.functions[match]]

            # Operator
            elif match in self.operators.keys():
                result += [self.operators[match]]

            # Constants
            elif match in self.constants.keys():
                result += [self.constants[match]]

            # Parentheses
            elif match in ('(', ')'):
                result += [match]

            # Probably a number
            else:
                try:
                    result += [float(match)]
                except ValueError:
                    pass

        return result


def main():
    '''
    Run the interactive calculator
    '''
    calc = Calculator()
    print('Disclaimer: The operator minus is written as "~"')
    print('Enter an equation')
    while True:
        try:
            equation = input('> ')
            arg_list = calc.parse_string_to_list(equation)
            calc.generate_output_queue(arg_list)
            res = calc.calculate()
            print(f'  {equation} = {res}')
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    main()
