import unittest
from hello import add, multiply


class TestAdd(unittest.TestCase):
    def test_positives(self):
        self.assertEqual(add(2, 3), 5)

    def test_negatives(self):
        self.assertEqual(add(-1, -5), -6)

    def test_mixed(self):
        self.assertEqual(add(-2, 5), 3)

    def test_zeros(self):
        self.assertEqual(add(0, 0), 0)

    def test_floats(self):
        self.assertAlmostEqual(add(1.5, 2.3), 3.8)


class TestMultiply(unittest.TestCase):
    def test_normal_cases(self):
        self.assertEqual(multiply(2, 3), 6)
        self.assertEqual(multiply(-1, 5), -5)

    def test_edge_cases(self):
        self.assertEqual(multiply(0, 0), 0)
        self.assertEqual(multiply(-2, -3), 6)


if __name__ == '__main__':
    unittest.main()
