import unittest
import math
import calculator
import numpy as np


class TestContainer(unittest.TestCase):

    def test_pop_empty_queue(self):
        queue = calculator.Queue()
        self.assertRaises(AssertionError, queue.pop)

    def test_pop_empty_stack(self):
        stack = calculator.Stack()
        self.assertRaises(AssertionError, stack.pop)

    def test_size_queue(self):
        queue = calculator.Queue()
        queue.push(1)
        self.assertEqual(1, queue.size())

    def test_size_stack(self):
        stack = calculator.Stack()
        stack.push(1)
        self.assertEqual(1, stack.size())

    def test_peek_queue(self):
        queue = calculator.Queue()
        queue.push(1)
        queue.push(2)
        self.assertEqual(1, queue.peek())

    def test_peek_stack(self):
        stack = calculator.Stack()
        stack.push(1)
        self.assertEqual(1, stack.peek())
        stack.push(2)
        self.assertEqual(2, stack.peek())

    def test_push_pop_queue(self):
        stack = calculator.Stack()
        stack.push(1)
        stack.push(2)
        self.assertEqual(2, stack.pop())

    def test_push_pop_stack(self):
        queue = calculator.Queue()
        queue.push(1)
        queue.push(2)
        self.assertEqual(1, queue.pop())


class TestOperator(unittest.TestCase):

    def test_add_op(self):
        add_op = calculator.Operator(operation=np.add)
        self.assertEqual(3, add_op.execute(1, 2))

    def test_subtract_op(self):
        subtract_op = calculator.Operator(operation=np.subtract)
        self.assertEqual(8, subtract_op.execute(10, 2))

    def test_multiply_op(self):
        multiply_op = calculator.Operator(operation=np.multiply)
        self.assertEqual(10, multiply_op.execute(5, 2))

    def test_divide_op(self):
        divide_op = calculator.Operator(operation=np.divide)
        self.assertEqual(5, divide_op.execute(10, 2))

    def test_add_and_multiply(self):
        add_op = calculator.Operator(operation=np.add)
        multiply_op = calculator.Operator(operation=np.multiply)
        self.assertEqual(20, multiply_op.execute(2, add_op.execute(5, 5)))


class TestCalculator(unittest.TestCase):

    def test_operators(self):
        calc = calculator.Calculator()
        self.assertEqual(2, calc.operators['+'].execute(1, 1))
        self.assertEqual(1, calc.operators['-'].execute(2, 1))
        self.assertEqual(8, calc.operators['*'].execute(2, 4))
        self.assertEqual(2, calc.operators['/'].execute(8, 4))

    def test_functions(self):
        calc = calculator.Calculator()
        self.assertAlmostEqual(
            0.0, calc.functions['COS'].execute(math.pi/2))

        self.assertAlmostEqual(
            1.0, calc.functions['SIN'].execute(math.pi/2))

        self.assertAlmostEqual(
            1.0, calc.functions['EXP'].execute(0))

        self.assertAlmostEqual(
            2.0, calc.functions['SQRT'].execute(4))

    def test_calculate(self):
        calc = calculator.Calculator()
        _input = [
            1, 2, 3, calc.operators['*'],
            calc.operators['+'], calc.functions['EXP']
        ]

        for elem in _input:
            calc.output_queue.push(elem)

        self.assertAlmostEqual(1096.633158428, calc.calculate())

    def test_generate_queue(self):
        calc = calculator.Calculator()
        _input = [
            calc.functions['EXP'], '(', '(',
            1, calc.operators['+'], 2, calc.operators['*'], 3, ')', ')'
        ]
        calc.generate_output_queue(_input)
        self.assertAlmostEqual(1096.633158428, calc.calculate())

    def test_calculator(self):
        calc = calculator.Calculator()
        _input = '((15 / (7 - (1 + 1))) * 3) - (2 + (1 + 1))'
        arg_list = calc.parse_string_to_list(_input)
        calc.generate_output_queue(arg_list)
        res = calc.calculate()
        self.assertEqual(5.0, res)

        _input = 'exp(1 + 2*3)'
        arg_list = calc.parse_string_to_list(_input)
        calc.generate_output_queue(arg_list)
        res = calc.calculate()
        self.assertAlmostEqual(1096.633158428, res)

        _input = 'cos(pi)'
        arg_list = calc.parse_string_to_list(_input)
        calc.generate_output_queue(arg_list)
        res = calc.calculate()
        self.assertAlmostEqual(-1.0, res)




