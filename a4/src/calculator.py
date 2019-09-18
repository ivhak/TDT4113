'''
Calculator that runs in a loop and evaluates expressions given by the user
'''

import math
import numbers
import re
import sys
import numpy as np


class Container:
    '''
    Super class for the different containers
    '''

    def __init__(self):
        self._items = []

    def size(self):
        ''' Return size of container '''
        return len(self._items)

    def is_empty(self):
        ''' Check if container is empty '''
        return len(self._items) == 0

    def push(self, item):
        ''' Add item to container '''
        self._items += [item]

    def pop(self):
        ''' Retrieve next item from container '''
        raise NotImplementedError

    def peek(self):
        ''' Return, but don't remove, next item from container '''
        raise NotImplementedError


class Queue(Container):
    '''
    Implementation of a FIFO queue
    '''

    def pop(self):
        assert not self.is_empty()
        first_it, *self._items = self._items
        return first_it

    def peek(self):
        assert not self.is_empty()
        return self._items[0]


class Stack(Container):
    '''
    Implemntation of a stack
    '''

    def pop(self):
        assert not self.is_empty()
        return self._items.pop()

    def peek(self):
        assert not self.is_empty()
        return self._items[self.size() - 1]


class Function():
    '''
    Wrapper for functions that operate on a single element
    '''

    def __init__(self, func):
        self.func = func

    def __repr__(self):
        return f'Function({self.func.__name__})'

    def __str__(self):
        return f'Function({self.func.__str__})'

    def execute(self, element, debug=False):
        '''
        Execute function on element and return result.
        '''

        # Check type
        if not isinstance(element, numbers.Number):
            raise TypeError('Cannot execute func if element is not a number')
        result = self.func(element)

        # Report
        if debug:
            print(f'Function: {self.func.__name__}({element:f}) = {result:f}')

        return result


class Operator():
    '''
    Wrapper for operators that operate on two elements
    '''

    def __init__(self, operation=None, strength=0):
        self.operation = operation
        self.strength = strength

    def __repr__(self):
        return f'Operator({self.operation.__name__})'

    def __str__(self):
        return f'Operator({self.operation.__str__})'

    def execute(self, first_elem, second_elem, debug=False):
        '''
        Execute operation on first_elem and second_elem and return the
        result
        '''

        # Check type of first element
        if not isinstance(first_elem, numbers.Number):
            raise TypeError(
                'Cannot execut operator, {first_elem} is not a number')

        # Check type of second element
        if not isinstance(second_elem, numbers.Number):
            raise TypeError(
                'Cannot execut operator, {second_elem} is not a number')

        result = self.operation(first_elem, second_elem)

        # Report
        if debug:
            print(f'Operation: {first_elem:f}'
                  f'{self.operation.__name__}{second_elem:f} = {result:f}')

        return result


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
            'SQRT': Function(np.sqrt)
        }

        self.constants = {
            'PI': math.pi,
            'TAU': math.tau
        }

        self.operators = {
            '+': Operator(np.add),
            '-': Operator(np.subtract),
            '/': Operator(np.divide),
            '^': Operator(np.power),
            '*': Operator(np.multiply)
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
        Converts a list of operators, functions, operands and parentheses from
        infix notation to reverse polish notation using the shunting-yard
        algorithm
        '''

        self.output_queue = Queue()
        op_stack = Stack()
        for elem in input_list:
            if isinstance(elem, numbers.Number):
                self.output_queue.push(elem)
            if isinstance(elem, (Function, Operator)):
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
        Parse input_str into a list of operators, operands, parentheses and
        functions, using regular expressions. Then substitute the functions and
        operand found with their corresponding Function/Operand object. Strings
        in the form of positive or negative ints or floats are converted to
        float.
        '''

        float_re = r'-?\d+\.\d+'
        int_re = r'-?\d+'
        paren_re = r'\(|\)'
        operator_re = r'\^|\+|\-|\*|/|'
        constans_re = '|'.join(self.constants.keys())
        fun_re = '|'.join(self.functions.keys())

        regex = '|'.join([float_re, int_re, paren_re,
                          operator_re, constans_re, fun_re])

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
            elif match in '()':
                result += [match]

            # Probably a number
            else:
                try:
                    result += [float(match)]
                except ValueError:
                    result += [match]

        return result


def main():
    '''
    Run the interactive calculator
    '''
    calc = Calculator()
    while True:
        try:
            print('Enter an equation')
            equation = input('> ')
            arg_list = calc.parse_string_to_list(equation)
            calc.generate_output_queue(arg_list)
            res = calc.calculate()
            print(f'{equation} = {res}')
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == '__main__':
    main()
