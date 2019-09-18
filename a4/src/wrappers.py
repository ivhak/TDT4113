'''
Wrappers for functions and operators used in calculator
'''
import numbers


class Function():
    '''
    Wrapper for functions that operate on a single element
    '''
    __slots__ = ['func']

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
    __slots__ = ['operation', 'strength']

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
                'Cannot execute operator, {first_elem} is not a number')

        # Check type of second element
        if not isinstance(second_elem, numbers.Number):
            raise TypeError(
                'Cannot execute operator, {second_elem} is not a number')

        result = self.operation(first_elem, second_elem)

        # Report
        if debug:
            print(f'Operation: {first_elem:f}'
                  f'{self.operation.__name__}{second_elem:f} = {result:f}')

        return result
