import unittest

from utils import cords_to_square, cords_to_square_2x2, cords_to_square_3x3, square_middle_to_cords


class TestSquareFunctions(unittest.TestCase):
    def test_cords_to_square(self):
        self.assertEqual(cords_to_square((0, 0), 10, 8), (0, 0))
        self.assertEqual(cords_to_square((5, 5), 10, 8), (0, 0))
        self.assertEqual(cords_to_square((10, 10), 10, 8), (1, 1))
        self.assertEqual(cords_to_square((15, 15), 10, 8), (1, 1))

    def test_cords_to_square_2x2(self):
        self.assertEqual(cords_to_square_2x2((5, 5), 10, 8), [(0, 0), (0, 0), (0, 0), (0, 0)])
        self.assertEqual(cords_to_square_2x2((10, 10), 10, 8), [(0, 0), (0, 1), (1, 0), (1, 1)])
        self.assertEqual(cords_to_square_2x2((11, 11), 10, 8), [(0, 0), (0, 1), (1, 0), (1, 1)])

    def test_cords_to_square_3x3(self):
        self.assertEqual(cords_to_square_3x3((10, 10), 10, 8),
                         [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)])
        self.assertEqual(cords_to_square_3x3((11, 11), 10, 8),
                         [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)])

    def test_square_to_middle_cords(self):
        self.assertEqual(square_middle_to_cords((0, 0), 10), (5.0, 5.0))
        self.assertEqual(square_middle_to_cords((1, 1), 10), (15.0, 15.0))
        self.assertEqual(square_middle_to_cords((2, 2), 10), (25.0, 25.0))
        self.assertEqual(square_middle_to_cords((0, 1), 10), (5.0, 15.0))
        self.assertEqual(square_middle_to_cords((1, 0), 10), (15.0, 5.0))
