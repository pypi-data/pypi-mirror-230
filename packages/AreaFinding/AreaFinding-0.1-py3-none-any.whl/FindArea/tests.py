import unittest
from FindArea import FindArea

class TestFindArea(unittest.TestCase):
    def setUp(self):
        self.findarea = FindArea()

    def test_triangle(self):
        self.assertEqual(self.findarea.triangle(6, 8, 10), 24.0)

    def test_circle(self):
        self.assertEqual(self.findarea.circle(0), 0)

if __name__ == "__main__":
  unittest.main()