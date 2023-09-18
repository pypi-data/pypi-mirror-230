import unittest
from src.kdistiller import train


class TestFoo(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(train.foo(1), 2)

    def test_zero(self):
        self.assertEqual(train.foo(0), 1)

    def test_negative(self):
        self.assertEqual(train.foo(-1), 0)


if __name__ == '__main__':
    unittest.main()
