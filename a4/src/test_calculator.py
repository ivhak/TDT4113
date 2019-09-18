import unittest
import math
import numpy as np
import calculator


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

    def test_operators_single(self):
        calc = calculator.Calculator()
        self.assertEqual(2, calc.operators['+'].execute(1, 1))
        self.assertEqual(1, calc.operators['~'].execute(2, 1))
        self.assertEqual(8, calc.operators['*'].execute(2, 4))
        self.assertEqual(2, calc.operators['/'].execute(8, 4))

    def test_functions_single(self):
        calc = calculator.Calculator()
        self.assertAlmostEqual(
            0.0, calc.functions['COS'].execute(math.pi/2))

        self.assertAlmostEqual(
            1.0, calc.functions['SIN'].execute(math.pi/2))

        self.assertAlmostEqual(
            1.0, calc.functions['EXP'].execute(0))

        self.assertAlmostEqual(
            2.0, calc.functions['SQRT'].execute(4))

    def test_generate_queue_1(self):
        calc = calculator.Calculator()
        _input = [
            1, 2, 3, calc.operators['*'],
            calc.operators['+'], calc.functions['EXP']
        ]

        for elem in _input:
            calc.output_queue.push(elem)

        self.assertAlmostEqual(1096.633158428, calc.calculate())

    def test_generate_queue_2(self):
        calc = calculator.Calculator()
        _input = [
            calc.functions['EXP'], '(', '(',
            1, calc.operators['+'], 2, calc.operators['*'], 3, ')', ')'
        ]
        calc.generate_output_queue(_input)
        self.assertAlmostEqual(1096.633158428, calc.calculate())

    def help_run_test(self, tests):
        calc = calculator.Calculator()
        for test in tests:
            arg_list = calc.parse_string_to_list(test[0])
            calc.generate_output_queue(arg_list)
            res = calc.calculate()
            self.assertAlmostEqual(test[1], res)

    def test_addition(self):
        tests = [
            ('2+2', 4),
            ('2  +  2', 4),
            ('2+2.', 4),
            ('3 + (5 + 1 + (2 + 2))', 13),
            ('1+2+4+8+16 + 11', 42),
            ('2.1+2.1', 4.2),
        ]
        self.help_run_test(tests)

    def test_division(self):
        tests = [
            ('1/2', 0.5),
            ('3.885 / 7', 0.555),
            ('(140/2)/0.5/2', 70),
            ('((517/4)/2/0.25/0.25)/22', 47),
            ('2987898/34743', 86),
        ]
        self.help_run_test(tests)

    def test_trig(self):
        tests = [
            ('cos(pi)', -1.0),
            ('cos(pi) * sin(pi)', 0.0),
            ('sin(pi)', 0),
            ('cos(pi)', -1),
            ('cos(tau)', 1),
            ('cos(2*pi)', 1),
            ('((2*pi / tau) + (10*pi))/(1+10*pi)', 1),
            ('pi * 2', 6.2831853071796),
            ('pi * pi', 9.8696044010894),
            ('2*pi*pi', 19.739208802179),
        ]
        self.help_run_test(tests)

    def test_multiplication(self):
        tests = [
            ('13 * 2', 26),
            ('3.2*2', 6.4),
            ('20*2*1.375', 55),
            ('0.75*((2*-4)*1.5)', -9),
            ('27*0.5', 13.5),
        ]
        self.help_run_test(tests)

    def test_functions(self):
        tests = [
            ("abs(-32)", 32),
            ("abs(-5~7)", 12),
            ("abs(-1.1)", 1.1),
            ("sqrt(100)", 10),
            ("SqRt(100)", 10),
            ("sqrt(sqrt(10000))", 10),
            ("sqrt(sqrt(10000) + 800)", 30),
            ("log(e)", 1),
            ("loG(E)", 1),
        ]
        self.help_run_test(tests)

    def test_random(self):
        tests = [
            ('(6/3)*5', 10.0),
            ('6+3*2', 12.0),
            ('((15 / (7 ~ (1 + 1))) * 3) ~ (2 + (1 + 1))', 5.0),
            ('exp(1 + 2*3)', 1096.633158428),
            ('12 ~ -3', 15.0),
        ]
        self.help_run_test(tests)
