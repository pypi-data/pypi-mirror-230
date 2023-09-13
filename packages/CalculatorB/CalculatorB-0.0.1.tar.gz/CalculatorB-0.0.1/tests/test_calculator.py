import unittest

from CalculatorB.Calculator.calculator import *


class Testsubstract(unittest.TestCase):

    def test_subtract(self):
        Calculator.reset()
        Calculator.add(10)
        result = Calculator.subtract(2)
        self.assertEqual(result, 8)


if __name__ == '__main__':
    unittest.main()


class Testadd(unittest.TestCase):
    def test_add(self):
        Calculator.reset()
        result = Calculator.add(2)
        self.assertEqual(result, 2)


if __name__ == '__main__':
    unittest.main()


class Testmultiply(unittest.TestCase):

    def test_multiply(self):
        Calculator.reset()
        Calculator.add(10)
        result = Calculator.multiply(2)
        self.assertEqual(result, 20)


if __name__ == '__main__':
    unittest.main()


class Testdivide(unittest.TestCase):

    def test_divide(self):
        Calculator.reset()
        Calculator.add(10)
        result = Calculator.divide(2)
        self.assertEqual(result, 5)


if __name__ == '__main__':
    unittest.main()


class Testnthroot(unittest.TestCase):

    def test_nthroot(self):
        Calculator.reset()
        Calculator.add(4)
        result = Calculator.nthroot(2)
        self.assertEqual(result, 2)


if __name__ == '__main__':
    unittest.main()


class Testreset(unittest.TestCase):

    def test_reset(self):
        Calculator.add(10)
        Calculator.reset()
        result = Calculator.reset()
        self.assertEqual(result, 0)


if __name__ == '__main__':
    unittest.main()
